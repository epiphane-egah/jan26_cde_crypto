import json
import os
 
from faker import Faker
 
CRYPTOS_DISPONIBLES = ["BTC", "ETH"]
 
 
def demander_informations_client():
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
        if name is None or usdt is None or crypto is None:
            name, usdt, crypto = demander_informations_client()
 
        if crypto not in CRYPTOS_DISPONIBLES:
            raise ValueError(f"Crypto non supportée : {crypto!r}")
 
        self.crypto = crypto
 
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
            self.solde_crypto = 0.0
            self.name = name
            # Mémorise l'orderId du dernier BUY non encore fermé par un SELL.
            # None = pas de position ouverte actuellement.
            self.id_ordre_ouverture_courant = None
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
 
        # Option A : on relie explicitement chaque SELL à l'ordre d'ouverture
        # correspondant, et on met à jour l'état pour le prochain appel.
        if order_type == "BUY":
            self.id_ordre_ouverture_courant = ordre["orderId"]
        elif order_type == "SELL":
            ordre["id_ordre_ouverture"] = self.id_ordre_ouverture_courant
            self.id_ordre_ouverture_courant = None  # position refermée
 
        self.save()
        return ordre
 
    def save(self):
        with open(self.save_path, "w") as f:
            json.dump(
                {
                    "usdt": self.usdt,
                    "solde_crypto": self.solde_crypto,
                    "crypto": self.crypto,
                    "name": self.name,
                    "id_ordre_ouverture_courant": self.id_ordre_ouverture_courant,
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
        self.id_ordre_ouverture_courant = data.get("id_ordre_ouverture_courant")
 
 
if __name__ == "__main__":
    client = Client()
    print(client.get_balance())