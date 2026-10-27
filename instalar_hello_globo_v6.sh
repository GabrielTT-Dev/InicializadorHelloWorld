#!/usr/bin/env bash
# Compatibilidade: a versão antiga trazia o hello_globo.py embutido num heredoc.
# Agora o código vive em hello_globo.py, então este script apenas chama o
# instalar.sh — assim as duas versões nunca ficam diferentes.
set -euo pipefail
cd "$(dirname "$0")"
exec bash ./instalar.sh "$@"
