#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

NAR_DIR="${PROJECT_ROOT}/nifi/extensions"
JDBC_DIR="${PROJECT_ROOT}/nifi/jdbc"

mkdir -p "${NAR_DIR}"
mkdir -p "${JDBC_DIR}"



download_if_missing() {
  local url="$1"
  local dest="$2"

  if [[ -f "$dest" ]]; then
    echo "  [skip] $dest already exists"
  else
    echo "  [download] $dest"
    curl -L "$url" -o "$dest"
  fi
}


echo ">>> Setting up..."
echo ">>> Starting downloading nifi dependecies..."
HIVE_SVC_API_URL="https://repo1.maven.org/maven2/org/apache/nifi/nifi-hive-services-api-nar/1.27.0/nifi-hive-services-api-nar-1.27.0.nar"
HIVE_SVC_API_FILE="${NAR_DIR}/nifi-hive-services-api-nar-1.27.0.nar"

HIVE_NAR_URL="https://repo1.maven.org/maven2/org/apache/nifi/nifi-hive-nar/1.27.0/nifi-hive-nar-1.27.0.nar"
HIVE_NAR_FILE="${NAR_DIR}/nifi-hive-nar-1.27.0.nar"

download_if_missing "$HIVE_SVC_API_URL" "$HIVE_SVC_API_FILE"
download_if_missing "$HIVE_NAR_URL"      "$HIVE_NAR_FILE"

HIVE_JDBC_URL="https://repo1.maven.org/maven2/org/apache/hive/hive-jdbc/3.1.3/hive-jdbc-3.1.3-standalone.jar"
HIVE_JDBC_FILE="${JDBC_DIR}/hive-jdbc-3.1.3-standalone.jar"

download_if_missing "$HIVE_JDBC_URL" "$HIVE_JDBC_FILE"
echo ">>> Done."


echo ">>> Starting downloading python dependecies..."
REQ_FILE="${PROJECT_ROOT}/requirements.txt"
VENV_DIR="${PROJECT_ROOT}/.venv"

if [[ -f "$REQ_FILE" ]]; then
  if [[ ! -d "$VENV_DIR" ]]; then
    python3 -m venv "$VENV_DIR"
  fi

  source "${VENV_DIR}/bin/activate"

  pip install --upgrade pip
  pip install -r "$REQ_FILE"

  deactivate
  echo ">>> Done."
else
  echo ">>> !!! Cannot find requirements.txt !!!"
fi


echo ">>> Building custom Hive2Dialect jar via sbt..."
SCALA_PROJECT_DIR="${PROJECT_ROOT}/spark/shit/custom_dialect"
SPARK_JARS_DIR="${PROJECT_ROOT}/spark/jars"

if ! command -v sbt >/dev/null 2>&1; then
  echo ">>> !!! sbt was not found in PATH, skip building Scala-project !!!"
  echo ">>> Donwload sbt and restart, please."
else
  if [[ ! -d "$SCALA_PROJECT_DIR" ]]; then
    echo ">>> !!! Scala-проект не найден по пути: $SCALA_PROJECT_DIR !!!"
  else
    echo "  [cd ] $SCALA_PROJECT_DIR"
    (
      cd "$SCALA_PROJECT_DIR"
      sbt package
    )

    mkdir -p "$SPARK_JARS_DIR"

    JAR_SRC="$(ls "$SCALA_PROJECT_DIR"/target/scala-2.12/*.jar 2>/dev/null | head -n 1 || true)"

    if [[ -z "$JAR_SRC" ]]; then
      echo ">>> !!! Cannot found jar in ${SCALA_PROJECT_DIR}/target/scala-2.12/"
    else
      echo "  [copy] $JAR_SRC -> $SPARK_JARS_DIR/"
      cp "$JAR_SRC" "$SPARK_JARS_DIR/"
      echo ">>> Scala jar is ready: $(basename "$JAR_SRC")"
    fi
  fi
fi

echo ">>> Job is done."
