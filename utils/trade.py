import json
from decimal import Decimal
 
import pandas as pd
import ta
 
from client import Client
 
MARGE_SECURITE_FRAIS = Decimal("0.999")  # laisse 0.1% de marge pour les frais
 
 
def update_balance(client, order):
    """
    Met à jour client.usdt et client.solde_crypto à partir du résultat
    d'un ordre exécuté. La comparaison des frais se fait dynamiquement
    contre client.crypto (ex: "BTC" ou "ETH"), plus jamais en dur.
    """
    executed_qty = Decimal(str(order["executedQty"]))
    quote_qty = Decimal(str(order["cummulativeQuoteQty"]))
 
    frais_crypto = sum(
        Decimal(str(f["commission"])) for f in order["fills"]
        if f["commissionAsset"] == client.crypto
    )
    frais_usdt = sum(
        Decimal(str(f["commission"])) for f in order["fills"]
        if f["commissionAsset"] == "USDT"
    )
 
    if order["side"] == "BUY":
        client.usdt -= float(quote_qty)
        client.usdt -= float(frais_usdt)
        client.solde_crypto += float(executed_qty)
        client.solde_crypto -= float(frais_crypto)
 
    elif order["side"] == "SELL":
        client.solde_crypto -= float(executed_qty)
        client.solde_crypto -= float(frais_crypto)
        client.usdt += float(quote_qty)
        client.usdt -= float(frais_usdt)
 
    client.save()
    return client
 
 
def save_order(order, path="transactions.jsonl"):
    with open(path, "a") as f:
        f.write(json.dumps(order) + "\n")
 
 
def trade(symbol, client):
    """
    symbol : ex. "BTCUSDT" — doit correspondre à client.crypto
    client : instance de Client déjà créée (nom, montant, crypto choisis
             une seule fois au démarrage, pas à chaque appel de trade())
    """
    data = get_historical_data(symbol, "1h", 650)
    df = pd.DataFrame(data)
 
    df["SM200"] = ta.trend.sma_indicator(df["close"], 200)
    df["SM600"] = ta.trend.sma_indicator(df["close"], 600)
 
    signal_achat = df["SM200"].iloc[-2] > df["SM600"].iloc[-2]
    signal_vente = df["SM200"].iloc[-2] < df["SM600"].iloc[-2]
 
    order = None
 
    if client.usdt > 5 and signal_achat:
        quantity = (client.usdt * float(MARGE_SECURITE_FRAIS)) / df["close"].iloc[-1]
        order = client.buy_or_sell("BUY", symbol, df, quantity)
        update_balance(client, order)
 
    elif client.solde_crypto > 0.0001 and signal_vente:
        quantity = client.solde_crypto  # on vend exactement ce qu'on possède
        order = client.buy_or_sell("SELL", symbol, df, quantity)
        update_balance(client, order)
 
    if order:
        save_order(order)
 
    return client
 
 
if __name__ == "__main__":
    client = Client()  # demande nom, montant, crypto une seule fois
    symbol = f"{client.crypto}USDT"
    trade(symbol, client)