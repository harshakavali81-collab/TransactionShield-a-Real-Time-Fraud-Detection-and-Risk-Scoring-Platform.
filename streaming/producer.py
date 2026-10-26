"""Publish deterministic, clearly synthetic events to a Kafka-compatible broker."""
import argparse
import json
import os
from ml.config import FEATURES
from ml.data.generate import create_synthetic


def demo_events(count=20, seed=42):
    frame = create_synthetic(n=count, seed=seed)
    numeric_ints = {"hour", "account_age_days", "velocity_24h", "prior_chargebacks",
                    "is_international", "is_new_device"}
    for _, row in frame.iterrows():
        event = {"transaction_id": str(row.transaction_id)}
        for key in FEATURES:
            value = row[key]
            event[key] = int(value) if key in numeric_ints else (
                float(value) if key in {"amount", "ip_risk_score"} else str(value))
        yield event


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--brokers", default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092"))
    parser.add_argument("--topic", default="transactionshield.demo")
    args = parser.parse_args()
    if not 1 <= args.count <= 10000:
        parser.error("count must be from 1 to 10000")
    from confluent_kafka import Producer
    producer = Producer({"bootstrap.servers": args.brokers})
    for event in demo_events(args.count, args.seed):
        producer.produce(args.topic, key=event["transaction_id"].encode(),
                         value=json.dumps(event).encode())
        producer.poll(0)
    remaining = producer.flush(30)
    if remaining:
        raise RuntimeError(f"{remaining} messages were not acknowledged")
    print(f"Published {args.count} synthetic events")


if __name__ == "__main__":
    main()
