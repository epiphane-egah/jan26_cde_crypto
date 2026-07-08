
import json
from decimal import Decimal
 
import pandas as pd
import ta
 
from client import Client
 
MARGE_SECURITE_FRAIS = Decimal("0.999")
 
 
def update_balance(client, order):
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
    """
    JSON Lines : un objet JSON complet par ligne. Chaque ligne correspond
    exactement à une future ligne de table SQL FAIT_SIGNAL_TRADING — c'est
    ce format qui permet de migrer vers SQL plus tard sans rien changer à
    la structure des données elles-mêmes (voir weekly_metrics.py).
    """
    with open(path, "a") as f:
        f.write(json.dumps(order) + "\n")
 
 
def trade(symbol, client):
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
        quantity = client.solde_crypto
        order = client.buy_or_sell("SELL", symbol, df, quantity)
        update_balance(client, order)
 
    if order:
        save_order(order)
 
    return client
 
 
if __name__ == "__main__":
    client = Client()
    symbol = f"{client.crypto}USDT"
    trade(symbol, client)
 