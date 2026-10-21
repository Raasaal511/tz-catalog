#!/usr/bin/env bash
set -euo pipefail

echo "==> API health"
curl -sf "http://localhost:8000/health" | tee /dev/stderr
echo

echo "==> Products list"
curl -sf "http://localhost:8000/api/v1/products" | tee /dev/stderr
echo

echo "==> Frontend"
curl -sf -o /dev/null -w "HTTP %{http_code}\n" "http://localhost:3000"

echo "OK"
