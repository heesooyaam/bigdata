#!/usr/bin/env bash
set -euo pipefail

echo ">>> Clearing ./nifi/metrics..."
if [ -d "./nifi/metrics" ]; then
  rm -rf ./nifi/metrics/*
fi
echo ">>> Done."

echo ">>> Clearing ./nifi/queries..."
if [ -d "./nifi/queries" ]; then
  rm -rf ./nifi/queries/*
fi
echo ">>> Done."
