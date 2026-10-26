"""At-least-once Kafka ingestion to FastAPI with replay-safe transaction IDs.

Requires `pip install -r requirements-streaming.txt` and a running broker.
The local synthetic demonstration uses plain transport; configure TLS/SASL for real brokers.
"""
import argparse
import json
import os
import requests
from confluent_kafka import Consumer, KafkaException


def process_message(raw: bytes, api_url: str, api_key: str = "", post=requests.post):
    event = json.loads(raw.decode("utf-8"))
    if not isinstance(event, dict) or not event.get("transaction_id"):
        raise ValueError("transaction_id required for replay-safe processing")
    headers = {"X-API-Key": api_key} if api_key else {}
    response = post(f"{api_url.rstrip('/')}/predict", json=event, headers=headers, timeout=10)
    if response.status_code in (201, 409):
        return response.status_code
    response.raise_for_status()
    return response.status_code


def main():
    parser = argparse.ArgumentParser(description="Consume synthetic events, persist scored transactions")
    parser.add_argument("--brokers", default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092"))
    parser.add_argument("--topic", default="transactionshield.demo")
    parser.add_argument("--group", default="transactionshield-demo-scorer")
    parser.add_argument("--api", default="http://localhost:8000")
    args = parser.parse_args()
    consumer = Consumer({"bootstrap.servers": args.brokers, "group.id": args.group,
                         "enable.auto.commit": False, "auto.offset.reset": "earliest"})
    consumer.subscribe([args.topic])
    print("Consuming synthetic transaction events; Ctrl+C to stop")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            try:
                status = process_message(msg.value(), args.api, os.getenv("API_KEY", ""))
                consumer.commit(message=msg, asynchronous=False)
                print(f"Committed partition={msg.partition()} offset={msg.offset()} HTTP={status}")
            except (ValueError, requests.RequestException) as exc:
                # No commit: message can be retried after repair. Avoid printing payloads.
                print(f"Ingestion halted before commit: {type(exc).__name__}: {exc}")
                raise
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
