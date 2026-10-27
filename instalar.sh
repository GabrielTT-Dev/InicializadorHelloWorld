#!/usr/bin/env bash
# Instala (ou atualiza) o Hello Globo no login do Linux Mint Cinnamon.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f hello_globo.py ]; then
    echo "Erro: hello_globo.py não encontrado. Rode este script dentro da pasta do projeto."
    exit 1
fi

DEST="$HOME/.local/share/hello-globo"
AUTO="$HOME/.config/autostart"

# Só chama o apt se faltar alguma coisa e, se falhar (offline, sem sudo),
# avisa em vez de abortar: normalmente já está tudo instalado.
FALTANDO=()
for pacote in python3-tk fonts-noto-core fonts-noto-cjk; do
    dpkg -s "$pacote" >/dev/null 2>&1 || FALTANDO+=("$pacote")
done
if [ ${#FALTANDO[@]} -gt 0 ]; then
    echo "Instalando dependências: ${FALTANDO[*]}"
    if ! sudo apt install -y "${FALTANDO[@]}"; then
        echo "Aviso: não foi possível instalar ${FALTANDO[*]}."
        echo "       O Hello Globo instala mesmo assim; sem python3-tk ele não roda e"
        echo "       sem as fontes Noto alguns alfabetos aparecem como quadradinhos."
    fi
fi

mkdir -p "$DEST" "$AUTO"
install -m 755 hello_globo.py "$DEST/hello_globo.py"

cat > "$AUTO/hello-globo.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Hello Globo
Comment=Animação de boas-vindas no login
Exec=python3 "$DEST/hello_globo.py"
Terminal=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=1
OnlyShowIn=X-Cinnamon;GNOME;
NoDisplay=true
DESKTOP

echo
echo "Instalado em $DEST"
echo "Para testar agora:  python3 $DEST/hello_globo.py"
echo "Para remover:       bash desinstalar.sh"
