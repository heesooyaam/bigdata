#!/usr/bin/env python3
import argparse
import time
from datetime import datetime
from typing import Dict, Any, List

import psutil
from kafka_utils import KafkaMetricsProducer

from config import DEFAULT_CONFIG, load_config_from_file, load_config_from_env, merge_configs
from collectors import collect_cpu, collect_ram, collect_disk, collect_net
from io_utils import format_metrics_line, write_line


def parse_args() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(
        description="Сервис для периодического сбора системных метрик."
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Путь к конфигурационному файлу (JSON)."
    )
    parser.add_argument(
        "--metrics",
        type=str,
        help="Список метрик через запятую: cpu,ram,disk,net."
    )
    parser.add_argument(
        "--interval",
        type=int,
        help="Интервал сбора в секундах."
    )
    parser.add_argument(
        "--output",
        type=str,
        help="'stdout' или путь к файлу для записи метрик."
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Собрать метрики один раз и завершить работу."
    )
    parser.add_argument(
        "--kafka",
        action="store_true",
        help="Включить отправку метрик в Apache Kafka."
    )
    parser.add_argument(
        "--kafka-bootstrap",
        type=str,
        help="Адрес(а) брокера Kafka, например 'localhost:9092'."
    )
    parser.add_argument(
        "--kafka-topic",
        type=str,
        help="Имя Kafka-топика для отправки метрик."
    )


    args = parser.parse_args()

    cli_cfg: Dict[str, Any] = {}

    if args.metrics:
        cli_cfg["metrics"] = [m.strip().lower() for m in args.metrics.split(",") if m.strip()]
    if args.interval is not None:
        cli_cfg["interval"] = args.interval
    if args.output:
        cli_cfg["output"] = args.output
    if args.kafka:
        cli_cfg["kafka_enabled"] = True
    if args.kafka_bootstrap:
        cli_cfg["kafka_bootstrap_servers"] = args.kafka_bootstrap
    if args.kafka_topic:
        cli_cfg["kafka_topic"] = args.kafka_topic

    return {
        "config_path": args.config,
        "cli_cfg": cli_cfg,
        "once": args.once,
    }


def main() -> None:
    args_parsed = parse_args()
    config_path = args_parsed["config_path"]
    cli_cfg = args_parsed["cli_cfg"]
    once = args_parsed["once"]

    file_cfg = load_config_from_file(config_path)
    env_cfg = load_config_from_env()
    config = merge_configs(DEFAULT_CONFIG, file_cfg, env_cfg, cli_cfg)

    kafka_enabled: bool = bool(config.get("kafka_enabled", False))
    kafka_bootstrap: str = str(config.get("kafka_bootstrap_servers", "localhost:9092"))
    kafka_topic: str = str(config.get("kafka_topic", "system-metrics"))

    metrics_to_collect: List[str] = config.get("metrics", [])
    interval: int = int(config.get("interval", 5))
    output: str = config.get("output", "stdout")

    print("===== Сервис сбора системных метрик =====")
    print(f"Метрики: {', '.join(metrics_to_collect)}")
    print(f"Интервал: {interval} с")
    print(f"Вывод: {output}")
    print("Нажмите Ctrl+C для остановки.\n")

    if kafka_enabled:
        print(f"Kafka: включено, bootstrap={kafka_bootstrap}, topic={kafka_topic}")
        kafka_producer = KafkaMetricsProducer(kafka_bootstrap, kafka_topic)
    else:
        print("Kafka: выключено")
        kafka_producer = None

    prev_net_counters = psutil.net_io_counters()

    try:
        while True:
            now = datetime.now()
            metrics_result: Dict[str, Any] = {}

            if "cpu" in metrics_to_collect:
                metrics_result.update(collect_cpu())
            if "ram" in metrics_to_collect:
                metrics_result.update(collect_ram())
            if "disk" in metrics_to_collect:
                metrics_result.update(collect_disk())
            if "net" in metrics_to_collect:
                metrics_result.update(collect_net(prev_net_counters))

            line = format_metrics_line(now, metrics_result)
            write_line(line, output)

            if kafka_producer is not None:
                payload = {
                    "timestamp": now.isoformat(),
                    **metrics_result,
                }
                kafka_producer.send(payload)

            if once:
                break

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nОстановка сервиса по Ctrl+C.")
    finally:
        if kafka_producer is not None:
            kafka_producer.close()


if __name__ == "__main__":
    main()
