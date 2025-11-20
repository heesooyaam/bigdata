#!/usr/bin/env bash
#set -e
#
#SPARK_SERVICE_NAME="spark"
#SPARK_CONTAINER_NAME="spark"
#SPARK_SCRIPT_NAME="net_ratio_10m.py"
#
#echo ">>> Starting ${SPARK_SERVICE_NAME}..."
#podman-compose up -d "${SPARK_SERVICE_NAME}"
#echo ">>> Done."
#
#echo ">>> Start ${SPARK_SCRIPT_NAME} inside ${SPARK_CONTAINER_NAME}..."
#podman exec -it "${SPARK_CONTAINER_NAME}" bash -lc "
#  set -e
#  /opt/spark/bin/spark-submit --master local[*] --jars /opt/jars/hive2-dialect_2.12-0.1.0.jar /opt/spark-apps/net_ratio_10m.py
#"
#echo ">>> Done."



set -e

SPARK_SERVICE_NAME="spark"
SPARK_CONTAINER_NAME="spark"
SPARK_SCRIPT_NAME="net_ratio_10m.py"

get_container_state() {
  if ! podman inspect -f '{{.State.Status}}' "${SPARK_CONTAINER_NAME}" 2>/dev/null; then
    echo "not-found"
  fi
}

echo ">>> Checking ${SPARK_CONTAINER_NAME} state..."
STATE="$(get_container_state)"

if [ "${STATE}" = "running" ]; then
  echo ">>> Container ${SPARK_CONTAINER_NAME} already running. Skipping podman-compose up."
else
  echo ">>> Starting ${SPARK_SERVICE_NAME} via podman-compose..."
  podman-compose up -d "${SPARK_SERVICE_NAME}"

  echo ">>> Waiting for ${SPARK_CONTAINER_NAME} to be running..."
  while true; do
    STATE="$(get_container_state)"
    if [ "${STATE}" = "running" ]; then
      echo ">>> ${SPARK_CONTAINER_NAME} is running."
      break
    fi
    if [ "${STATE}" = "exited" ] || [ "${STATE}" = "dead" ]; then
      echo "!!! Container ${SPARK_CONTAINER_NAME} is in bad state: ${STATE}"
      exit 1
    fi
    sleep 1
  done
fi

echo ">>> Start ${SPARK_SCRIPT_NAME} inside ${SPARK_CONTAINER_NAME}..."
podman exec -it "${SPARK_CONTAINER_NAME}" bash -lc "
  set -e
  /opt/spark/bin/spark-submit \
    --master local[*] \
    --jars /opt/jars/hive2-dialect_2.12-0.1.0.jar \
    /opt/spark-apps/${SPARK_SCRIPT_NAME}
"
echo ">>> Done."
