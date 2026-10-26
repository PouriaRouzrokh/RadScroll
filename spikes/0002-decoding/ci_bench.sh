#!/usr/bin/env bash
# One bench call for the CI workflow: appends its JSON rows to out/<name>.jsonl (and prints them), keeps stderr in
# out/<name>-<engine>.log, and on Linux records peak memory and any kill in out/<name>-time.log.
# Usage: ci_bench.sh <name> <clips_dir> <engine> [bench args...]
set -uo pipefail
name=$1
shift
mkdir -p out
cmd=(python -I "$(dirname "$0")/bench.py" "$@")
if [ "$(uname)" = Linux ]; then
  echo "== $*" >> "out/$name-time.log"
  cmd=(/usr/bin/time -v -a -o "out/$name-time.log" "${cmd[@]}")
fi
"${cmd[@]}" 2>> "out/$name-$2.log" | tee -a "out/$name.jsonl"
