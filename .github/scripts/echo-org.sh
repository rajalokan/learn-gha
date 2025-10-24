#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <org-name>" >&2
  exit 1
fi

org="$1"

echo "Running script for organization: ${org}"
