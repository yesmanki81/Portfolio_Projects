# click_event_producer.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from kafka import KafkaProducer
import json, os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (if using .env)
load_dotenv()
EC2_HOST = os.getenv("EC2_HOST", "localhost")

# Kafka config
KAFKA_BROKER = f"{EC2_HOST}:9092"
TOPIC = "gameevents"  # Kafka topic name

# Flask app setup
app = Flask(__name__)
CORS(app)

# Kafka Producer setup
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8")
)

@app.route("/click", methods=["GET"])
def handle_click():
    # Extract query parameters
    user = request.args.get("user", "MysteryHand")
    user_choice = request.args.get("user_choice")
    computer_choice = request.args.get("computer_choice")
    result = request.args.get("result")

    # Validation
    if not user_choice or not computer_choice or not result:
        return jsonify({"error": "Missing one or more required parameters"}), 400

    # Build Kafka event payload
    event = {
        "user": user,
        "user_choice": user_choice,
        "computer_choice": computer_choice,
        "result": result,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    # Send to Kafka
    print("📩 Sending event to Kafka:", event)
    producer.send(TOPIC, event)
    producer.flush()

    return jsonify({"status": "ok"}), 200

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

