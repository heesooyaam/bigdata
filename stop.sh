#!/usr/bin/env bash

cd "$(dirname "$0")" || exit

echo ">>> Stopping podman services..."
podman-compose down
echo ">>> Done."

echo ">>> Stopping podman machine..."
podman machine stop
echo ">>> Done."

