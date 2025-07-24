# crypto_consumer.py
from kafka import KafkaConsumer
import psycopg2
import json

consumer = KafkaConsumer(
    'cryptoPrices',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

conn = psycopg2.connect(
    dbname='cryptodb',
    user='crypto',
    password='crypto123',
    host='localhost'
)
cur = conn.cursor()
for msg in consumer:
    data = msg.value
    symbol = data['symbol']
    timestamp = data['timestamp']
    price = data['price']

    cur.execute("""
        INSERT INTO crypto_prices (symbol, timestamp, price)
        VALUES (%s, %s, %s)
    """, (symbol, timestamp, price))

    conn.commit()
    print(f"Inserted: {symbol} @ {timestamp} = {price}")