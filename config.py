import json
import os
from typing import Dict, Any


DEFAULT_CONFIG: Dict[str, Any] = {
    "metrics": ["cpu", "ram", "disk", "net"],
    "interval": 5,
    "output": "stdout",

    "kafka_enabled": False,
    "kafka_bootstrap_servers": "localhost:29092",
    "kafka_topic": "system-metrics",
}


def load_config_from_file(path: str | None) -> Dict[str, Any]:
    if not path:
        return {}
    if not os.path.exists(path):
        print(f"[WARN] Конфигурационный файл {path} не найден, используются значения по умолчанию.")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Ошибка чтения конфигурационного файла {path}: {e}")
        return {}


def load_config_from_env() -> Dict[str, Any]:
    """
    Поддерживаются переменные окружения:
      METRICS, INTERVAL, OUTPUT
      KAFKA_ENABLED (true/false/1/0)
      KAFKA_BOOTSTRAP_SERVERS (например, 'localhost:9092')
      KAFKA_TOPIC (например, 'system-metrics')
    """
    cfg: Dict[str, Any] = {}

    metrics_env = os.getenv("METRICS")
    if metrics_env:
        cfg["metrics"] = [m.strip().lower() for m in metrics_env.split(",") if m.strip()]

    interval_env = os.getenv("INTERVAL")
    if interval_env:
        try:
            cfg["interval"] = int(interval_env)
        except ValueError:
            print(f"[WARN] Невозможно преобразовать INTERVAL={interval_env} к int, игнорируется.")

    output_env = os.getenv("OUTPUT")
    if output_env:
        cfg["output"] = output_env

    kafka_enabled = os.getenv("KAFKA_ENABLED")
    if kafka_enabled is not None:
        cfg["kafka_enabled"] = kafka_enabled.lower() in ("1", "true", "yes")

    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if kafka_bootstrap:
        cfg["kafka_bootstrap_servers"] = kafka_bootstrap

    kafka_topic = os.getenv("KAFKA_TOPIC")
    if kafka_topic:
        cfg["kafka_topic"] = kafka_topic

    return cfg


def merge_configs(
    default_cfg: Dict[str, Any],
    file_cfg: Dict[str, Any],
    env_cfg: Dict[str, Any],
    cli_cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Приоритет: CLI > ENV > FILE > DEFAULT
    """
    cfg = default_cfg.copy()
    for src in (file_cfg, env_cfg, cli_cfg):
        for k, v in src.items():
            if v is not None:
                cfg[k] = v
    return cfg
