import json
import os
 
from faker import Faker
 
CRYPTOS_DISPONIBLES = ["BTC", "ETH"]
 
 
def demander_informations_client():
    """Demande interactivement le nom, le montant à investir et la crypto."""
    nom = input("Nom du client (laisser vide pour un nom aléatoire) : ").strip()
    if not nom:
        nom = Faker("fr_FR").name()
 
    while True:
        montant_str = input("Montant à investir en USDT : ").strip()
        try:
            montant = float(montant_str)
            if montant <= 0:
                print("Le montant doit être strictement positif.")
                continue
            break
        except ValueError:
            print("Merci d'entrer un nombre valide (ex: 1000).")
 
    while True:
        crypto = input(f"Crypto à trader ({'/'.join(CRYPTOS_DISPONIBLES)}) : ").strip().upper()
        if crypto in CRYPTOS_DISPONIBLES:
            break
        print(f"Choix invalide. Choisis parmi : {', '.join(CRYPTOS_DISPONIBLES)}")
 
    return nom, montant, crypto
 
 
class Client:
    def __init__(self, name=None, usdt=None, crypto=None, save_path=None):
        """
        Deux façons de créer un client :
 
        1. Interactif :  Client()
           -> demande le nom, le montant et la crypto via input()
 
        2. Programmatique (utile pour les tests / plusieurs bots automatisés) :
           Client(name="Alice", usdt=1000, crypto="BTC")
        """
        if name is None or usdt is None or crypto is None:
            name, usdt, crypto = demander_informations_client()
 
        if crypto not in CRYPTOS_DISPONIBLES:
            raise ValueError(f"Crypto non supportée : {crypto!r}")
 
        self.crypto = crypto  # ex: "BTC" — quelle crypto ce client trade
 
        if save_path is None:
            nom_fichier = name.replace(" ", "_")
            save_path = f"client_{nom_fichier}_{crypto}.json"
        self.save_path = save_path
 
        if os.path.exists(self.save_path):
            self._load()
            print(f"Solde existant chargé pour {self.name} "
                  f"({self.usdt:.2f} USDT / {self.solde_crypto:.6f} {self.crypto})")
        else:
            self.usdt = float(usdt)
            self.solde_crypto = 0.0  # nom générique, valable pour BTC, ETH, etc.
            self.name = name
            self.save()
            print(f"Nouveau client créé : {self.name} -> {self.save_path}")
 
    def get_balance(self):
        return {"usdt": self.usdt, self.crypto: self.solde_crypto}
 
    def buy_or_sell(self, order_type, symbol, df, quantite):
        if order_type not in ("BUY", "SELL"):
            raise ValueError(f"order_type invalide : {order_type!r}")
 
        ordre = simulate_order(
            df=df,
            symbol=symbol,
            side=order_type,
            client_order_id=f"bot_{self.name}",
            quantite=quantite,
        )
        return ordre
 
    def save(self):
        with open(self.save_path, "w") as f:
            json.dump(
                {
                    "usdt": self.usdt,
                    "solde_crypto": self.solde_crypto,
                    "crypto": self.crypto,
                    "name": self.name,
                },
                f,
                indent=2,
            )
 
    def _load(self):
        with open(self.save_path) as f:
            data = json.load(f)
        self.usdt = data["usdt"]
        self.solde_crypto = data["solde_crypto"]
        self.name = data["name"]
        self.crypto = data.get("crypto", self.crypto)
 
 
if __name__ == "__main__":
    client = Client()
    print(client.get_balance())