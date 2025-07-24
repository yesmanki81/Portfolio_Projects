
# 📊 Real-Time Bitcoin & Ethereum Dashboard on AWS EC2

This project collects real-time cryptocurrency prices (BTC, ETH), streams them via Kafka, stores them in PostgreSQL, and visualizes both real and predicted prices using Grafana.

---

## ⚙️ Architecture

```
[Python Producer] → [Kafka] → [Python Consumer] → [PostgreSQL] → [Grafana Dashboard]
```

---

## 🚀 Stack

- **Data Source**: CryptoCompare API (`requests`)
- **Streaming**: Apache Kafka
- **Storage**: PostgreSQL
- **Prediction**: Python (Simple Moving Average)
- **Visualization**: Grafana
- **Environment**: Ubuntu 22.04 on AWS EC2

---

## 📦 Quick Setup

### 1. Kafka

```bash
# Download Kafka
wget https://downloads.apache.org/kafka/3.7.2/kafka_2.12-3.7.2.tgz
tar -xzf kafka_2.12-3.7.2.tgz && cd kafka
# Start services
nohup bin/zookeeper-server-start.sh config/zookeeper.properties &
nohup bin/kafka-server-start.sh config/server.properties &
# Create topic
bin/kafka-topics.sh --create --topic crypto_prices --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### 2. PostgreSQL

```sql
CREATE DATABASE cryptodb;
CREATE USER crypto WITH PASSWORD 'crypto123';
GRANT ALL PRIVILEGES ON DATABASE cryptodb TO crypto;

\c cryptodb
CREATE TABLE crypto_prices (
  symbol TEXT, timestamp TIMESTAMP, price FLOAT
);
CREATE TABLE crypto_prediction (
  symbol TEXT, timestamp TIMESTAMP, predicted_price FLOAT
);
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crypto;
```

### 3. Python Scripts

- **Producer**: Sends BTC/ETH price to Kafka every 5 seconds
- **Consumer**: Reads from Kafka and inserts into PostgreSQL
- **Predictor**: Calculates 5-min SMA every 10 seconds and stores predictions

```bash
pip install kafka-python psycopg2-binary requests
python crypto_producer.py
python crypto_consumer.py
python price_predictor.py
```

---

## 📈 Grafana Setup

- Install Grafana: `sudo apt install grafana`
- Run: `http://<EC2_IP>:3000` (default: admin / admin)
- Add PostgreSQL as Data Source
- Create dashboards:
  - Real-time price (Time Series)
  - Prediction line overlay
  - 24h high/low (Stat)
  - % change (Bar Chart)

---

## ✅ Sample Query

**Real-time BTC price**  
```sql
SELECT $__time(timestamp), price FROM crypto_prices WHERE symbol='BTC'
```

**Predicted BTC price**  
```sql
SELECT $__time(timestamp), predicted_price FROM crypto_prediction WHERE symbol='BTC'
```

---

## 🙌 Result

A full-stack, real-time crypto dashboard showing actual and predicted prices for BTC and ETH, built with open-source tools on AWS EC2.

