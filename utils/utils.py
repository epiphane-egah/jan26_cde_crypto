import requests
import json
import datetime
import time

def get_data(symbol, interval, start_time, end_time):
    # url = "https://api.binance.com/api/v3/ticker/price"
    url = "https://api.binance.com/api/v3/klines"
    
    result = []
    
    while start_time < end_time:
        params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time,
        "limit": 1000
        }


        response = requests.get(url, params=params)

        time.sleep(60)

        
        data = response.json()
        
        if not data:
            break
        
        for k in data:
            candle = {
                "open_time": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5])
            }
            
            result.append(candle)


        
        interval_ms = convert_in_ms(interval)
        start_time =  data[-1][0] + interval_ms

    return result

def convert_in_ms(interval: str):
    if interval == "1m":
        return 60*1000
    elif interval == "1h":
        return 3600*1000
    elif interval == "1d":
        return 24*3600*1000

def get_crypto_price(symbol):
    url = "https://api.binance.com/api/v3/ticker/price"

    try:
        response = requests.get(url, params={"symbol": symbol.upper()}, timeout=10)
        response.raise_for_status()

        data = response.json()

        if "price" not in data:
            print(f"Erreur : symbole '{symbol}' introuvable.")
            return

        return data

    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion : {e}")

def get_historical_data(symbol, interval, nb_data):
    end_time = int(datetime.datetime.today().timestamp()*1000)
    start_time = end_time - convert_in_ms(interval) * nb_data
    return get_data(symbol, interval, start_time = start_time, end_time = end_time)

