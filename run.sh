#!/usr/bin/env sh
set -eu
case "${1:-}" in
  model) python3 -m src.model ;;
  server) python3 -m src.server ;;
  demo) python3 -m src.demo_rpc ;;
  test) coverage run --branch -m pytest && coverage report -m ;;
  *) echo "Usage: ./run.sh model|server|demo|test"; exit 2 ;;
esac
