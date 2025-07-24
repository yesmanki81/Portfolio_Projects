# 🎮 RealTime User Behavior Analytics Insights

A real-time user behavior analytics pipeline built with **Kafka → Spark → PostgreSQL → Grafana**, designed to capture and visualize Rock-Paper-Scissors game interactions from a browser-based UI.

---

## ✅ Project Overview

This project demonstrates a real-time user activity analytics system using Apache Kafka, Spark Streaming, PostgreSQL, and Grafana on AWS EC2 instances. The data source is a HTML-based Rock-Paper-Scissors game, which sends interaction data to Kafka via a Flask server.

---

## ⚙️ Tech Stack

- **Apache Kafka + Zookeeper** – Message broker for game event streaming
- **Apache Spark Streaming** – Stream processing and transformation
- **PostgreSQL** – Persistent storage for event logs
- **Grafana** – Real-time data visualization
- **Flask** – Kafka producer for sending game events
- **HTML** – Rock-Paper-Scissors UI frontend
- **AWS EC2** – Cloud infrastructure

---

## 🛠 Architecture

```plaintext
[Game UI] → [Flask Kafka Producer] → [Kafka Topic] → [Spark Streaming] → [PostgreSQL] → [Grafana]


## 🧪 How It Works
- 1.Players play the Rock-Paper-Scissors game on a web interface.
- 2.Each game result is sent to a Flask server, which publishes it to a Kafka topic.
- 3.Spark Streaming consumes the Kafka topic and parses the event data.
- 4.The processed data is stored in PostgreSQL.
- 5.Grafana visualizes various metrics from the stored data.
