#!/usr/bin/env bash
set -euo pipefail

# Entry point for publishing the Study Review Desk as a Domino App.
# To try it in a workspace first:  PORT=8501 bash exercises/c_StudyReviewApp/app.sh

PORT="${PORT:-${1:-8888}}"

# Run from the project root so the app can import the shared code in common/.
cd "$(dirname "$0")/../.."

exec streamlit run exercises/c_StudyReviewApp/app.py \
  --server.address 0.0.0.0 \
  --server.port "$PORT" \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  --browser.gatherUsageStats false \
  --theme.primaryColor "#543FDD" \
  --theme.backgroundColor "#FFFFFF" \
  --theme.secondaryBackgroundColor "#FAFAFA" \
  --theme.textColor "#2E2E38"
