# kafka_utils.py
from typing import Dict, Any

import json
from kafka import KafkaProducer


class KafkaMetricsProducer:
    """
    Простая обёртка над KafkaProducer для отправки метрик в JSON-формате.
    """
    def __init__(self, bootstrap_servers: str, topic: str):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def send(self, payload: Dict[str, Any]) -> None:
        """
        Отправить одно сообщение в Kafka.
        """
        self.producer.send(self.topic, payload)

    def close(self) -> None:
        self.producer.flush()
        self.producer.close()
