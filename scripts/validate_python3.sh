#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "[*] Python 3 compile checks..."
python3 -m py_compile artillery.py restart_server.py remove_ban.py setup.py src/*.py

echo "[*] Integration tests..."
python3 -m unittest tests/test_setup_non_interactive.py tests/test_iptables_parsing.py

echo "[*] Non-interactive installer smoke test..."
if command -v timeout >/dev/null 2>&1; then
  timeout 5 python3 setup.py --non-interactive
else
  python3 - <<'PY'
import subprocess
subprocess.run(["python3", "setup.py", "--non-interactive"], check=True, timeout=5)
PY
fi

echo "[*] Python 2 legacy pattern scan..."
if rg -n -e 'raw_input|print "|except [^\n]*, [^\n]*:|SocketServer|urllib2|email\.MIME' -e '(^|[^[:alnum:]_])file\(' *.py src/*.py; then
  echo "[!] Legacy Python 2 patterns detected."
  exit 1
fi

echo "[*] Diff hygiene check..."
git diff --check

echo "[+] Validation completed successfully."
