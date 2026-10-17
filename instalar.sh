#!/usr/bin/env bash
# Instala o Hello Globo no login do Linux Mint Cinnamon.
set -e
cd "$(dirname "$0")"

if [ ! -f hello_globo.py ]; then
    echo "Erro: hello_globo.py não encontrado. Rode este script dentro da pasta do projeto."
    exit 1
fi

DEST="$HOME/.local/share/hello-globo"
AUTO="$HOME/.config/autostart"

sudo apt install -y python3-tk fonts-noto-core fonts-noto-cjk

mkdir -p "$DEST" "$AUTO"
cp hello_globo.py "$DEST/hello_globo.py"
chmod +x "$DEST/hello_globo.py"

cat > "$AUTO/hello-globo.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Hello Globo
Comment=Animação de boas-vindas no login
Exec=python3 $DEST/hello_globo.py
X-GNOME-Autostart-enabled=true
NoDisplay=true
DESKTOP

echo
echo "Instalado! Para testar agora:  python3 $DEST/hello_globo.py"
echo "Para remover:  bash desinstalar.sh"
