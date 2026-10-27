#!/usr/bin/env python3
"""Animação de login: "hello world" em vários idiomas formando um globo.

A animação fica na tela girando até você apertar Enter.
"""
import colorsys
import getpass
import math
import os
import random
import socket
import time
import tkinter as tk
from collections import deque
from tkinter import font as tkfont

SAUDACOES = [
    "Hello World", "Olá Mundo", "Hola Mundo", "Bonjour le monde",
    "Hallo Welt", "Ciao mondo", "Hej världen", "Hallo wereld",
    "Witaj świecie", "Привет, мир", "Γειά σου Κόσμε", "こんにちは世界",
    "你好，世界", "안녕하세요 세계", "Marhaba bil-alam", "Shalom olam",
    "Namaste Duniya", "Merhaba Dünya", "Xin chào thế giới", "Halo Dunia",
    "Kamusta Mundo", "Habari Dunia", "Sawubona Mhlaba", "Hei maailma",
    "Hej verden", "Hei verden", "Ahoj světe", "Helló világ",
    "Salut lume", "Здравей свят", "Pozdrav svijete", "Sveikas pasauli",
    "Sveika pasaule", "Tere maailm", "Salam donya", "Bula Vuravura",
    "Aloha Honua", "Kia ora Ao", "Dia duit a dhomhain", "Bore da fyd",
    "Ola mundo", "Hola món", "Mondua aupa", "Selam Dunya",
    "Zdravo svete", "Përshëndetje botë", "Hello Mundo", "Saluton mondo",
]

# ---------- ajustes ----------
INTERVALO_MS = 16        # alvo de ~60 quadros por segundo
T_DIGITA = 1.5           # digitando "hello world"
T_PAUSA = 0.35           # "Enter"
T_TITULO = 1.6           # "Hello World" grande no meio da tela
T_ENTRADA = 3.2          # palavras saindo do título e se encaixando na esfera
T_FADE = 1.0             # globo se abre e some depois do Enter
VEL_GIRO = 0.45          # radianos por segundo
INCLINACAO = math.radians(18)
ESPACO_LINHAS = 2.7      # distância entre linhas de texto (em alturas de letra); maior = mais leve
DURACAO_VOO = T_ENTRADA * 0.6

# O globo é montado em fatias durante a digitação do terminal, em vez de tudo de
# uma vez: assim a janela abre na hora e não trava no primeiro segundo.
ORCAMENTO_MONTAGEM_MS = 4.0
PRAZO_MONTAGEM = T_DIGITA + T_PAUSA + T_TITULO - 0.2   # tudo pronto antes do 1º voo

MOSTRAR_DICA = True
DICA = "pressione Enter para continuar"
TECLAS_SAIR = ("<Return>", "<KP_Enter>")

_n = math.sqrt(0.35 ** 2 + 0.35 ** 2 + 0.85 ** 2)
LUZ = (-0.35 / _n, 0.35 / _n, 0.85 / _n)   # luz de frente, um pouco de cima à esquerda


def ease_out(t):
    return 1 - (1 - t) ** 3


def limitar(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def hexa(r, g, b):
    return "#%02x%02x%02x" % (
        int(limitar(r, 0, 255)), int(limitar(g, 0, 255)), int(limitar(b, 0, 255)))


class Palavra:
    __slots__ = ("ix", "iy", "atraso", "curva", "voa",
                 "anel", "texto", "wpx", "s")


class Letra:
    __slots__ = ("item", "sl", "cl", "cphi", "z0", "y0", "ox", "pal", "idx",
                 "anel", "balde", "vis", "chave")


class Globo:
    def __init__(self):
        self.root = tk.Tk()
        self.ativo = True
        self.pronto = False
        self.saindo = False
        self.t_saida = 0.0
        self.alfa = 0.0

        r = self.root
        r.title("Hello Globo")
        r.configure(bg="black", cursor="none")
        try:
            r.attributes("-type", "splash")
        except tk.TclError:
            pass
        r.attributes("-fullscreen", True)
        r.attributes("-topmost", True)
        try:
            r.attributes("-alpha", 0.0)
        except tk.TclError:
            pass
        r.update_idletasks()
        self.w = r.winfo_screenwidth()
        self.h = r.winfo_screenheight()
        self.cv = tk.Canvas(r, width=self.w, height=self.h, bg="black",
                            highlightthickness=0, cursor="none")
        self.cv.pack(fill="both", expand=True)
        for seq in TECLAS_SAIR:
            r.bind_all(seq, self.sair)
        r.protocol("WM_DELETE_WINDOW", self.sair)
        r.focus_force()

        self.ct, self.st = math.cos(INCLINACAO), math.sin(INCLINACAO)
        self.escala = self.h / 1080
        self.raio = min(self.w, self.h) * 0.35
        self.cx = self.w / 2
        self.cy = self.h / 2 + self.h * 0.02
        self.cores = {}
        self.letras = []
        self._preparar()

        # prompt estilo terminal
        self.prompt_txt = f"{getpass.getuser()}@{socket.gethostname()}:~$ hello world"
        self.prompt = self.cv.create_text(
            int(self.w * 0.04), int(self.h * 0.06), anchor="nw", text="",
            fill="#33ff66",
            font=tkfont.Font(family="Monospace", size=-max(12, int(22 * self.escala))))
        self._prompt_ok = False

        # "Hello World" grande no meio da tela (as outras palavras saem dele)
        self.titulo_txt = "Hello World"
        self.titulo = self.cv.create_text(
            self.cx, self.cy, anchor="center", text="", fill="black",
            font=tkfont.Font(family="Sans", size=-max(24, int(68 * self.escala)),
                             weight="bold"))
        self._titulo_ok = False

        # dica discreta no rodapé depois que o globo se forma
        self.dica = self.cv.create_text(
            self.cx, int(self.h * 0.93), anchor="center", text=DICA, fill="black",
            font=tkfont.Font(family="Monospace", size=-max(11, int(15 * self.escala))))
        self._dica_q = -1

        self.quadros = 0
        self.t0 = time.perf_counter()
        self.root.after(INTERVALO_MS, self.quadro)

    # ---------- montagem do globo, em fatias ----------
    def _preparar(self):
        """Parte barata da montagem: fontes, medidas e a fila de anéis."""
        self.base = max(10, int(19 * self.escala))
        self.fontes = [tkfont.Font(family="Sans", size=-max(7, int(self.base * f)),
                                   weight="bold")
                       for f in (1.0, 0.9, 0.8, 0.7)]
        self._larg_cache = {}
        self._larg_pal = {}
        self._passo = ESPACO_LINHAS * self.base / self.raio
        n_meio = int(math.radians(72) / self._passo)
        self._aneis = list(range(-n_meio, n_meio + 1))
        self._anel_idx = 0
        self._anel_atual = None
        self._fila = deque()
        self._pool = []
        self._gap_min = self.base * 1.0
        self._anel_hello = round(INCLINACAO / self._passo)
        self._sphi = {}
        self._reabastecer()

    def _larg(self, ch):
        w = self._larg_cache.get(ch)
        if w is None:
            w = self._larg_cache[ch] = max(2, self.fontes[0].measure(ch))
        return w

    def _larg_palavra(self, p):
        w = self._larg_pal.get(p)
        if w is None:
            w = self._larg_pal[p] = sum(self._larg(ch) for ch in p)
        return w

    def _reabastecer(self):
        nova = [x for x in SAUDACOES if x != "Hello World"]
        random.shuffle(nova)
        self._pool.extend(nova)

    def _preparar_anel(self, anel):
        """Distribui as palavras de uma linha de latitude (só cálculo, sem Tk)."""
        R = self.raio
        passo = self._passo
        phi = anel * passo
        cphi = math.cos(phi)
        sphi = math.sin(phi)
        C = 2 * math.pi * R * cphi

        hello = anel == self._anel_hello
        escolhidas = []
        usados = set()
        soma = 0
        gap_min = self._gap_min
        if hello:
            w_h = self._larg_palavra("Hello World")
            escolhidas.append(("Hello World", w_h))
            usados.add("Hello World")
            soma = w_h

        while True:
            if len(self._pool) < 12:
                self._reabastecer()
            achou = None
            for j in range(min(8, len(self._pool))):
                p = self._pool[j]
                if p in usados:
                    continue
                wpx = self._larg_palavra(p)
                if soma + wpx + gap_min * (len(escolhidas) + 1) <= C:
                    achou = (self._pool.pop(j), wpx)
                    break
            if achou is None:
                break
            escolhidas.append(achou)
            usados.add(achou[0])
            soma += achou[1]

        if not escolhidas:
            return

        gap = (C - soma) / len(escolhidas)
        s = random.uniform(0, C)
        if hello:
            s = (-escolhidas[0][1] / 2) % C   # palavra centrada de frente
        for n_pal, (texto, wpx) in enumerate(escolhidas):
            especial = hello and n_pal == 0
            # a palavra voa se estiver virada para o observador no começo
            lc = (s + wpx / 2) / (R * cphi)
            z1c = cphi * math.cos(lc)
            x1c = cphi * math.sin(lc)
            y2c = sphi * self.ct - z1c * self.st
            z2c = sphi * self.st + z1c * self.ct
            pal = Palavra()
            pal.texto, pal.wpx, pal.s, pal.anel = texto, wpx, s, anel
            # todas começam no centro da tela, junto do título
            pal.ix = self.cx + random.uniform(-60, 60) * self.escala
            pal.iy = self.cy + random.uniform(-25, 25) * self.escala
            pal.curva = random.uniform(-0.45, 0.45)
            pal.voa = z2c > 0.12
            d = min(1.0, math.hypot(x1c, y2c))
            pal.atraso = (d * T_ENTRADA * 0.28 + random.uniform(0, T_ENTRADA * 0.12)
                          if pal.voa else 0.0)
            if especial:
                pal.ix, pal.iy, pal.curva, pal.atraso = self.cx, self.cy, 0.0, 0.0
            self._fila.append(pal)
            s += wpx + gap

    def _criar_palavra(self, pal):
        """Cria os itens de canvas de uma palavra (parte caríssima da montagem)."""
        R = self.raio
        phi = pal.anel * self._passo
        cphi, sphi = math.cos(phi), math.sin(phi)
        z0, y0 = sphi * self.st, sphi * self.ct
        f0 = self.fontes[0]
        desloc = 0
        s, wpx = pal.s, pal.wpx
        for idx, ch in enumerate(pal.texto):
            w = self._larg(ch)
            if ch != " ":
                lon = (s + desloc + w / 2) / (R * cphi)
                L = Letra()
                L.item = self.cv.create_text(0, 0, text=ch, fill="black",
                                             font=f0, state="hidden")
                L.sl, L.cl = math.sin(lon), math.cos(lon)
                L.cphi, L.z0, L.y0 = cphi, z0, y0
                L.ox = desloc + w / 2 - wpx / 2
                L.pal, L.idx = pal, idx
                L.anel = pal.anel
                L.balde, L.vis, L.chave = 0, False, None
                self.letras.append(L)
            desloc += w

    def _construir(self, orcamento_ms):
        """Cria o globo em pedaços, sem travar o quadro."""
        inicio = time.perf_counter()
        limite = orcamento_ms / 1000.0
        while True:
            if not self._fila:
                if self._anel_idx >= len(self._aneis):
                    self.pronto = True
                    return
                self._preparar_anel(self._aneis[self._anel_idx])
                self._anel_idx += 1
                if not self._fila:
                    continue
            while self._fila:
                self._criar_palavra(self._fila.popleft())
                if time.perf_counter() - inicio >= limite:
                    return

    # ---------- cores ----------
    def cor(self, anel, nb, nf):
        chave = (anel, nb, nf)
        c = self.cores.get(chave)
        if c is None:
            c = self.cores[chave] = self._calcular_cor(anel, nb, nf)
        return c

    def _calcular_cor(self, anel, nb, nf):
        # matiz pela latitude: azul no norte -> verde -> laranja no sul
        sphi = self._sphi.get(anel)
        if sphi is None:
            sphi = self._sphi[anel] = math.sin(anel * self._passo)
        matiz = 0.60 - 0.52 * (1 - sphi) / 2
        f = nf / 6
        v = limitar(nb / 15 + 0.5 * f)
        rr, gg, bb = colorsys.hsv_to_rgb(matiz, 0.88 - 0.6 * f, v)
        return hexa(rr * 255, gg * 255, bb * 255)

    # ---------- controle ----------
    def sair(self, _evento=None):
        """Enter: começa o fade. A janela só fecha no fim dele."""
        if self.ativo and not self.saindo:
            self.saindo = True
            self.t_saida = time.perf_counter()

    def _fechar(self):
        if not self.ativo:
            return
        self.ativo = False
        if os.environ.get("GLOBO_DEBUG"):
            dur = max(time.perf_counter() - self.t0, 1e-6)
            print(f"letras={len(self.letras)} quadros={self.quadros} "
                  f"fps={self.quadros / dur:.1f} dur={dur:.1f}s")
        self.root.destroy()

    # ---------- quadro ----------
    def quadro(self):
        if not self.ativo:
            return
        inicio = time.perf_counter()
        t = inicio - self.t0
        self.quadros += 1

        # monta o restante do globo durante a digitação do terminal
        if not self.pronto:
            falta = PRAZO_MONTAGEM - t
            self._construir(1e9 if falta <= 0 else ORCAMENTO_MONTAGEM_MS)

        t_tit = t - T_DIGITA - T_PAUSA      # relógio do título
        t_ent = t_tit - T_TITULO            # relógio da saída das palavras
        fade = limitar((inicio - self.t_saida) / T_FADE) if self.saindo else 0.0
        if fade >= 1.0:
            self._fechar()
            return
        vida = 1 - fade
        espalha = 1 + 0.9 * fade * fade   # globo se abre no final

        # transparência da janela: entra suave, sai suave
        alfa = min(limitar(t / 0.35), vida)
        if abs(alfa - self.alfa) > 0.01:
            self.alfa = alfa
            try:
                self.root.attributes("-alpha", alfa)
            except tk.TclError:
                pass

        # prompt digitando
        k = 1 - 0.6 * limitar(t_tit / 2.0)
        if t_tit < 2.0:
            n = int(limitar(t / (T_DIGITA * 0.85)) * len(self.prompt_txt))
            cursor = "█" if (int(t * 3) % 2 == 0 and t_tit < 0.5) else " "
            self.cv.itemconfig(self.prompt, text=self.prompt_txt[:n] + cursor,
                               fill=hexa(51 * k, 255 * k, 102 * k))
        elif not self._prompt_ok:
            self._prompt_ok = True
            self.cv.itemconfig(self.prompt, text=self.prompt_txt,
                               fill=hexa(51 * k, 255 * k, 102 * k))

        # título: digita no meio da tela e se desfaz quando as palavras saem dele
        if t_ent < 0.9:
            n_t = int(limitar(t_tit / 0.8) * len(self.titulo_txt)) if t_tit >= 0 else 0
            e = (1 - limitar(t_ent / 0.9)) * vida
            e *= 0.92 + 0.08 * math.sin(t * 7)
            self.cv.itemconfig(self.titulo, text=self.titulo_txt[:n_t],
                               fill=hexa(225 * e, 250 * e, 255 * e))
        elif not self._titulo_ok:
            self._titulo_ok = True
            self.cv.itemconfig(self.titulo, text=self.titulo_txt, fill="black")

        # dica do rodapé (só muda quando o brilho muda)
        if MOSTRAR_DICA:
            a = limitar((t_ent - T_ENTRADA) / 0.8) * vida
            q = int(a * (0.72 + 0.28 * math.sin(t * 2.0)) * 20)
            if q != self._dica_q:
                self._dica_q = q
                b = q / 20.0
                self.cv.itemconfig(self.dica, fill=hexa(120 * b, 150 * b, 160 * b))

        # giro com partida suave
        tg = max(0.0, t_ent - T_ENTRADA * 0.95)
        spin = VEL_GIRO * (tg + 0.8 * (math.exp(-tg / 0.8) - 1))
        cs, sn = math.cos(spin), math.sin(spin)
        ct, st = self.ct, self.st
        R = self.raio * espalha
        cx, cy = self.cx, self.cy
        lx, ly, lz = LUZ
        cv = self.cv
        fontes = self.fontes
        cor = self.cor
        aparece = limitar((t_ent - T_ENTRADA) / 0.8)

        for L in self.letras:
            if L.item is None:
                continue
            z1 = L.cphi * (L.cl * cs - L.sl * sn)
            z2 = L.z0 + z1 * ct
            pal = L.pal
            tl = t_ent - pal.atraso
            if z2 <= 0.14 or t_ent < 0 or (pal.voa and tl < 0) or (not pal.voa and aparece <= 0):
                if L.vis:
                    L.vis = False
                    cv.itemconfig(L.item, state="hidden")
                continue

            x1 = L.cphi * (L.sl * cs + L.cl * sn)
            y2 = L.y0 - z1 * st
            alvo_x = cx + R * x1
            alvo_y = cy - R * y2

            if pal.voa:
                prog = ease_out(limitar(tl / DURACAO_VOO))
            else:
                prog = 1.0
            if prog < 1.0:
                ix, iy = pal.ix + L.ox * 0.15, pal.iy
                dx, dy = alvo_x - ix, alvo_y - iy
                arco = math.sin(math.pi * prog) * pal.curva
                px = ix + dx * prog - dy * arco
                py = iy + dy * prog + dx * arco
            else:
                px, py = alvo_x, alvo_y

            # luz + escurecimento nas bordas
            lamb = x1 * lx + y2 * ly + z2 * lz
            lamb = lamb ** 0.8 if lamb > 0 else 0.0
            lf = limitar((z2 - 0.14) / 0.42)
            lf = lf * lf * (3 - 2 * lf)
            b = (0.45 + 0.55 * lamb) * lf * limitar(prog * 1.5) * vida
            if not pal.voa:
                b *= aparece
            flash = 0.0
            if pal.voa and tl < DURACAO_VOO + 0.6:
                flash = max(0.0, 1 - abs(tl - L.idx * 0.025 - DURACAO_VOO) / 0.6)
            chave = (int(b * 15 + 0.5), int(flash * 6 + 0.5))
            balde = 0 if z2 > 0.8 else 1 if z2 > 0.55 else 2 if z2 > 0.3 else 3

            mudou_cor = chave != L.chave
            mudou_fonte = balde != L.balde
            if mudou_cor or mudou_fonte or not L.vis:
                kw = {}
                if mudou_cor:
                    L.chave = chave
                    kw["fill"] = cor(L.anel, chave[0], chave[1])
                if mudou_fonte:
                    L.balde = balde
                    kw["font"] = fontes[balde]
                if not L.vis:
                    L.vis = True
                    kw["state"] = "normal"
                cv.itemconfig(L.item, **kw)
            cv.coords(L.item, px, py)

        # se o quadro demorou, devolve pelo menos 4 ms para o resto do sistema
        # (compositor, teclado) em vez de emendar um quadro no outro
        gasto = (time.perf_counter() - inicio) * 1000
        espera = int(INTERVALO_MS - gasto)
        if espera < 4:
            espera = 4
        self.root.after(espera, self.quadro)


if __name__ == "__main__":
    Globo().root.mainloop()
