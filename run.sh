#!/usr/bin/env bash

set -e

cd "$(dirname "$0")"

echo ">>> Podman machine starting..."
podman machine start >/dev/null 2>&1 || true
echo ">>> Done."

echo ">>> Setting up containers..."
podman-compose up -d
sleep 10
echo ">>> Done."
