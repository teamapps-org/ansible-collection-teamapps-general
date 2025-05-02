#!/bin/bash
set -e

response=$(exec 3<>/dev/tcp/localhost/9080 && \
  echo -e "GET /ready HTTP/1.1\r\nHost: localhost\r\n\r\n" >&3 && \
  head -n1 <&3)

if echo "$response" | grep -q "200 OK"; then
    echo "Healthcheck passed: $response"
    exit 0
else
    echo "Healthcheck failed: $response"
    exit 1
fi
