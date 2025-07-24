# crypto_prediction.py
import psycopg2
from datetime import datetime
import time
from sklearn.linear_model import LinearRegression
import numpy as np
 
def predict_and_store():
    try:
        conn = psycopg2.connect(
            dbname="cryptodb",
            user="crypto",
            password="crypto123",
            host="localhost"
        )
        cur = conn.cursor()
 
        def predict_price(symbol):
            cur.execute("""
                SELECT EXTRACT(EPOCH FROM timestamp), price
                FROM crypto_prices
                WHERE symbol = %s AND timestamp >= NOW() - INTERVAL '30 minutes'
                ORDER BY timestamp
            """, (symbol,))
            data = cur.fetchall()
            if len(data) < 2:
               return None
 
            times = [[float(row[0])] for row in data] 
            prices = [float(row[1]) for row in data] 
 
            model = LinearRegression()
            model.fit(times, prices)
 
            future_time = [[times[-1][0] + 60]]
            predicted_price = model.predict(future_time)[0]
            return round(float(predicted_price), 2)
 
        for symbol in ['BTC', 'ETH']:
            predicted = predict_price(symbol)
            if predicted:
                cur.execute("""
                    INSERT INTO crypto_prediction (symbol, timestamp, predicted_price)
                    VALUES (%s, %s, %s)
                """, (symbol, datetime.now().replace(microsecond=0), predicted))
                print(f"[✓] Predicted {symbol} price in 1 min: {predicted:.2f}")
 
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[✗] Error: {e}")
 
while True:
    predict_and_store()
    time.sleep(120)