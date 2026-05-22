#!/usr/bin/env bash

BASE="http://127.0.0.1:8000"

echo "================================="
echo "CPU Sequential"
echo "================================="

wrk -t8 -c100 -d20s \
${BASE}/cpu-seq

echo ""
echo "================================="
echo "CPU Threaded"
echo "================================="

wrk -t8 -c100 -d20s \
${BASE}/cpu-thread

echo ""
echo "================================="
echo "IO Bound"
echo "================================="

wrk -t8 -c200 -d20s \
${BASE}/io

echo ""
echo "================================="
echo "Mixed"
echo "================================="

wrk -t8 -c100 -d20s \
${BASE}/mixed