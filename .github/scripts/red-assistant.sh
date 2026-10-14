#!/usr/bin/env bash

set -euo pipefail

echo "Red assistant received a request."
echo "Repository: ${GITHUB_REPOSITORY}"
echo "Pull request: #${PR_NUMBER}"
echo "Requested by: @${COMMENT_AUTHOR}"
echo "Demo command completed successfully."
