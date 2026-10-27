#!/usr/bin/env bash
# Remove o Hello Globo do login.
set -u
pkill -f "$HOME/.local/share/hello-globo/hello_globo.py" 2>/dev/null
rm -f "$HOME/.config/autostart/hello-globo.desktop"
rm -rf "$HOME/.local/share/hello-globo"
echo "Hello Globo removido."
