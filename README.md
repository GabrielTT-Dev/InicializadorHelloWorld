# 🌍 Hello Globo

Animação de boas-vindas para o login do **Linux Mint (Cinnamon)**.

Ao entrar com a senha, um `hello world` é digitado no terminal, um **"Hello World" grande** aparece no meio da tela e, a partir dele, "hello world" em dezenas de idiomas surge e se encaixa na superfície de um **globo girando**, feito só de palavras. Depois o globo se abre, some em fade e a área de trabalho aparece normalmente.

## Requisitos

- Linux Mint com Cinnamon (testado em ambiente X11)
- Python 3 com Tkinter (`python3-tk`)
- Fontes Noto, para os alfabetos não latinos (`fonts-noto-core`, `fonts-noto-cjk`)

## Instalação

```bash
git clone https://github.com/SEU-USUARIO/hello-globo.git
cd hello-globo
bash instalar.sh
```

O script instala as dependências, copia o `hello_globo.py` para `~/.local/share/hello-globo/` e cria a entrada de inicialização automática em `~/.config/autostart/`. No próximo login a animação roda sozinha.

## Testar sem reiniciar

```bash
python3 ~/.local/share/hello-globo/hello_globo.py
```

Dá para pular a animação com **Esc** ou com um clique.

## Remover

```bash
bash desinstalar.sh
```

## Ajustes

No topo do `hello_globo.py` há algumas constantes:

| Constante | O que faz |
|---|---|
| `T_TITULO` | Tempo do "Hello World" grande no meio da tela |
| `T_ENTRADA` | Tempo das palavras saindo do título e formando o globo |
| `T_GIRA` | Tempo do globo girando |
| `VEL_GIRO` | Velocidade do giro |
| `INCLINACAO` | Inclinação do eixo do globo |
| `ESPACO_LINHAS` | Distância entre as linhas de texto. Aumente (ex.: `3.6`) se estiver pesado no seu PC |

Para ver quantos quadros por segundo você está tendo:

```bash
GLOBO_DEBUG=1 python3 ~/.local/share/hello-globo/hello_globo.py
```

## Como funciona

Cada letra é um item de um `Canvas` do Tkinter posicionado em uma esfera 3D (linhas de latitude, eixo inclinado). A cada quadro, a esfera é girada, projetada na tela e iluminada, e só o lado virado para você é desenhado. O visual é todo feito em Python puro, sem bibliotecas externas.

## Licença

[MIT](LICENSE)
