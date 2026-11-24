"""Bibliothèque de figures SVG pour les items préparés hors plateforme.

Toutes les figures sont tracées par code à partir de données exactes : repères et courbes, histogrammes, tableaux,
circuits, optique, forces, échiquiers de croisement, frises… Sortie : chaîne SVG autonome (viewBox, polices système),
sans script, lisible hors ligne et redimensionnable.
"""
from __future__ import annotations

import math
import uuid
from typing import Callable, Sequence

NUIT, OR, VERT, ROUGE, GRIS, GRILLE, ENCRE = "#1B2A4A", "#B8922E", "#2E7D5B", "#B23A3A", "#7A8290", "#E3DED2", "#1E2433"
FONT = "font-family='Public Sans, Helvetica, Arial, sans-serif'"


def uid() -> str:
    """Suffixe unique pour les identifiants internes (plusieurs figures peuvent cohabiter sur une même page)."""
    return uuid.uuid4().hex[:6]


def esc(s) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w: int, h: int, inner: str) -> str:
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' {FONT} font-size='13'>"
            f"<rect width='{w}' height='{h}' fill='#fff'/>{inner}</svg>")


def txt(x, y, s, size=13, anchor="middle", color=ENCRE, weight="normal", italic=False, rotate=None) -> str:
    rot = f" transform='rotate({rotate} {x} {y})'" if rotate is not None else ""
    st = " font-style='italic'" if italic else ""
    return f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' fill='{color}' font-weight='{weight}'{st}{rot}>{esc(s)}</text>"


def fmt(v: float) -> str:
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:g}".replace(".", ",")


# ------------------------------------------------------------------ repère et courbes

class Plot:
    """Repère orthogonal avec graduations ; convertit des coordonnées mathématiques en pixels."""

    def __init__(self, x0, x1, y0, y1, w=460, h=320, ml=52, mr=18, mt=18, mb=46, xstep=1, ystep=1, xlabel="x", ylabel="y",
                 grid=True, arrows=True, xfmt: Callable | None = None, yfmt: Callable | None = None):
        self.x0, self.x1, self.y0, self.y1, self.w, self.h = x0, x1, y0, y1, w, h
        self.ml, self.mr, self.mt, self.mb = ml, mr, mt, mb
        self.parts: list[str] = []
        self.xfmt, self.yfmt = xfmt or fmt, yfmt or fmt
        self.u = uid()
        self._axes(xstep, ystep, xlabel, ylabel, grid, arrows)

    def X(self, x):
        return self.ml + (x - self.x0) / (self.x1 - self.x0) * (self.w - self.ml - self.mr)

    def Y(self, y):
        return self.h - self.mb - (y - self.y0) / (self.y1 - self.y0) * (self.h - self.mt - self.mb)

    def _axes(self, xstep, ystep, xlabel, ylabel, grid, arrows):
        p = self.parts
        xa = self.Y(0) if self.y0 <= 0 <= self.y1 else self.Y(self.y0)
        ya = self.X(0) if self.x0 <= 0 <= self.x1 else self.X(self.x0)
        k = math.ceil(self.x0 / xstep)
        while k * xstep <= self.x1 + 1e-9:
            x = k * xstep
            if grid:
                p.append(f"<line x1='{self.X(x):.1f}' y1='{self.mt}' x2='{self.X(x):.1f}' y2='{self.h - self.mb}' stroke='{GRILLE}' stroke-width='1'/>")
            if abs(x) > 1e-9 or not (self.x0 <= 0 <= self.x1):
                p.append(f"<line x1='{self.X(x):.1f}' y1='{xa - 4:.1f}' x2='{self.X(x):.1f}' y2='{xa + 4:.1f}' stroke='{ENCRE}'/>")
                p.append(txt(self.X(x), xa + 17, self.xfmt(x), 12))
            k += 1
        k = math.ceil(self.y0 / ystep)
        while k * ystep <= self.y1 + 1e-9:
            y = k * ystep
            if grid:
                p.append(f"<line x1='{self.ml}' y1='{self.Y(y):.1f}' x2='{self.w - self.mr}' y2='{self.Y(y):.1f}' stroke='{GRILLE}' stroke-width='1'/>")
            if abs(y) > 1e-9 or not (self.y0 <= 0 <= self.y1):
                p.append(f"<line x1='{ya - 4:.1f}' y1='{self.Y(y):.1f}' x2='{ya + 4:.1f}' y2='{self.Y(y):.1f}' stroke='{ENCRE}'/>")
                p.append(txt(ya - 8, self.Y(y) + 4, self.yfmt(y), 12, "end"))
            k += 1
        u = self.u
        ar = f"marker-end='url(#fl{u})'" if arrows else ""
        p.insert(0, f"<defs><marker id='fl{u}' markerWidth='8' markerHeight='8' refX='6' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='{ENCRE}'/></marker>"
                    f"<marker id='flr{u}' markerWidth='8' markerHeight='8' refX='6' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='{ROUGE}'/></marker>"
                    f"<marker id='fln{u}' markerWidth='8' markerHeight='8' refX='6' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='{NUIT}'/></marker>"
                    f"<marker id='flv{u}' markerWidth='8' markerHeight='8' refX='6' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='{VERT}'/></marker>"
                    f"<clipPath id='cp{u}'><rect x='{self.ml}' y='{self.mt - 2}' width='{self.w - self.ml - self.mr}' height='{self.h - self.mt - self.mb + 4}'/></clipPath></defs>")
        p.append(f"<line x1='{self.ml}' y1='{xa:.1f}' x2='{self.w - self.mr + 6}' y2='{xa:.1f}' stroke='{ENCRE}' stroke-width='1.4' {ar}/>")
        p.append(f"<line x1='{ya:.1f}' y1='{self.h - self.mb}' x2='{ya:.1f}' y2='{self.mt - 6}' stroke='{ENCRE}' stroke-width='1.4' {ar}/>")
        p.append(txt(self.w - self.mr + 6, min(xa + 34, self.h - 4), xlabel, 13, "end", italic=True))
        p.append(txt(ya + 10, self.mt + 2, ylabel, 13, "start", italic=True))
        if self.y0 <= 0 <= self.y1 and self.x0 <= 0 <= self.x1:
            p.append(txt(ya - 7, xa + 15, "O", 12, "end"))

    def curve(self, f: Callable[[float], float], a=None, b=None, n=300, color=NUIT, width=2.2, dash=None, clip=True):
        a = self.x0 if a is None else a
        b = self.x1 if b is None else b
        pts, segs = [], []
        for i in range(n + 1):
            x = a + (b - a) * i / n
            try:
                y = f(x)
            except (ValueError, ZeroDivisionError, OverflowError):
                y = None
            if y is None or (clip and not (self.y0 - 0.5 * (self.y1 - self.y0) <= y <= self.y1 + 0.5 * (self.y1 - self.y0))) or math.isnan(y):
                if pts:
                    segs.append(pts)
                pts = []
                continue
            pts.append((self.X(x), self.Y(min(max(y, self.y0 - 0.3 * (self.y1 - self.y0)), self.y1 + 0.3 * (self.y1 - self.y0)))))
        if pts:
            segs.append(pts)
        d = f" stroke-dasharray='{dash}'" if dash else ""
        for s in segs:
            self.parts.append(f"<polyline clip-path='url(#cp{self.u})' fill='none' stroke='{color}' stroke-width='{width}'{d} stroke-linejoin='round' points='" +
                              " ".join(f"{x:.1f},{y:.1f}" for x, y in s) + "'/>")
        return self

    def polyline(self, pts: Sequence[tuple], color=NUIT, width=2.2, dash=None, close=False, fill=None):
        d = f" stroke-dasharray='{dash}'" if dash else ""
        tag = "polygon" if close else "polyline"
        self.parts.append(f"<{tag} fill='{fill or 'none'}' stroke='{color}' stroke-width='{width}'{d} points='" +
                          " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in pts) + "'/>")
        return self

    def area(self, f, a, b, color=OR, opacity=0.28, n=200):
        pts = [(a, 0)] + [(a + (b - a) * i / n, f(a + (b - a) * i / n)) for i in range(n + 1)] + [(b, 0)]
        self.parts.append(f"<polygon fill='{color}' fill-opacity='{opacity}' stroke='none' points='" +
                          " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in pts) + "'/>")
        return self

    def point(self, x, y, label=None, color=NUIT, dx=8, dy=-8, r=4, anchor="start"):
        self.parts.append(f"<circle cx='{self.X(x):.1f}' cy='{self.Y(y):.1f}' r='{r}' fill='{color}'/>")
        if label:
            self.parts.append(txt(self.X(x) + dx, self.Y(y) + dy, label, 13, anchor, color, "bold"))
        return self

    def dashes_to_axes(self, x, y, color=GRIS):
        self.parts.append(f"<polyline fill='none' stroke='{color}' stroke-width='1.2' stroke-dasharray='4 3' points='{self.X(x):.1f},{self.Y(0 if self.y0 <= 0 else self.y0):.1f} {self.X(x):.1f},{self.Y(y):.1f} {self.X(0 if self.x0 <= 0 else self.x0):.1f},{self.Y(y):.1f}'/>")
        return self

    def segment(self, x1, y1, x2, y2, color=NUIT, width=2, dash=None, arrow=False):
        d = f" stroke-dasharray='{dash}'" if dash else ""
        m = {NUIT: "fln", ROUGE: "flr", VERT: "flv"}.get(color, "fl") + self.u
        ar = f" marker-end='url(#{m})'" if arrow else ""
        self.parts.append(f"<line x1='{self.X(x1):.1f}' y1='{self.Y(y1):.1f}' x2='{self.X(x2):.1f}' y2='{self.Y(y2):.1f}' stroke='{color}' stroke-width='{width}'{d}{ar}/>")
        return self

    def label(self, x, y, s, color=ENCRE, size=13, anchor="start", weight="normal", italic=False):
        self.parts.append(txt(self.X(x), self.Y(y), s, size, anchor, color, weight, italic))
        return self

    def bars(self, data: Sequence[tuple], width=0.7, color=NUIT, labels=True):
        for x, v in data:
            x1, x2 = self.X(x - width / 2), self.X(x + width / 2)
            self.parts.append(f"<rect x='{x1:.1f}' y='{self.Y(v):.1f}' width='{x2 - x1:.1f}' height='{self.Y(0) - self.Y(v):.1f}' fill='{color}' fill-opacity='0.85'/>")
            if labels:
                self.parts.append(txt((x1 + x2) / 2, self.Y(v) - 5, fmt(v), 12))
        return self

    def legend(self, entries: Sequence[tuple], x=None, y=None):
        x = x if x is not None else self.w - self.mr - 150
        y = y if y is not None else self.mt + 8
        out = [f"<rect x='{x - 6}' y='{y - 4}' width='156' height='{18 * len(entries) + 6}' fill='#fff' fill-opacity='0.9' stroke='{GRILLE}'/>"]
        for i, (lab, col, dash) in enumerate(entries):
            d = f" stroke-dasharray='{dash}'" if dash else ""
            out.append(f"<line x1='{x}' y1='{y + 8 + 18 * i}' x2='{x + 26}' y2='{y + 8 + 18 * i}' stroke='{col}' stroke-width='2.4'{d}/>")
            out.append(txt(x + 32, y + 12 + 18 * i, lab, 12, "start"))
        self.parts += out
        return self

    def render(self) -> str:
        return svg(self.w, self.h, "".join(self.parts))


# ------------------------------------------------------------------ tableau

def table(headers: Sequence[str], rows: Sequence[Sequence], col_w: int | Sequence[int] = 90, row_h=28, title=None, first_col_bold=False) -> str:
    n = len(headers)
    ws = [col_w] * n if isinstance(col_w, int) else list(col_w)
    W = sum(ws) + 2
    top = 30 if title else 1
    H = top + row_h * (len(rows) + 1) + 1
    out = []
    if title:
        out.append(txt(W / 2, 20, title, 13, weight="bold"))
    x = 1
    for j, h in enumerate(headers):
        out.append(f"<rect x='{x}' y='{top}' width='{ws[j]}' height='{row_h}' fill='{NUIT}' stroke='#fff'/>")
        out.append(txt(x + ws[j] / 2, top + row_h / 2 + 5, h, 12.5, color="#fff", weight="bold"))
        x += ws[j]
    for i, r in enumerate(rows):
        x = 1
        y = top + row_h * (i + 1)
        for j, c in enumerate(r):
            out.append(f"<rect x='{x}' y='{y}' width='{ws[j]}' height='{row_h}' fill='{'#F7F4EC' if i % 2 else '#fff'}' stroke='{GRILLE}'/>")
            out.append(txt(x + ws[j] / 2, y + row_h / 2 + 5, c, 13, weight="bold" if (first_col_bold and j == 0) else "normal"))
            x += ws[j]
    return svg(W, H, "".join(out))


# ------------------------------------------------------------------ secteurs

def pie(values: Sequence[tuple], w=420, h=260, r=100) -> str:
    total = sum(v for _, v in values)
    cx, cy = 130, h / 2
    cols = [NUIT, OR, VERT, ROUGE, GRIS, "#6C8EBF", "#A66DB0"]
    out, a0 = [], -math.pi / 2
    for i, (lab, v) in enumerate(values):
        a1 = a0 + 2 * math.pi * v / total
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        large = 1 if a1 - a0 > math.pi else 0
        out.append(f"<path d='M{cx},{cy} L{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f} z' fill='{cols[i % len(cols)]}' stroke='#fff' stroke-width='2'/>")
        am = (a0 + a1) / 2
        out.append(txt(cx + 0.62 * r * math.cos(am), cy + 0.62 * r * math.sin(am) + 4, f"{100 * v / total:.0f} %".replace(".", ","), 12, color="#fff", weight="bold"))
        out.append(f"<rect x='{cx + r + 40}' y='{40 + 22 * i}' width='14' height='14' fill='{cols[i % len(cols)]}'/>")
        out.append(txt(cx + r + 60, 52 + 22 * i, lab, 13, "start"))
        a0 = a1
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ arbre de probabilités

def tree(branches: Sequence[tuple], w=480, h=300) -> str:
    """branches : [(label1, p1, [(label2, p2), ...]), ...] — deux niveaux."""
    out = []
    x0, x1, x2 = 40, 190, 370
    n1 = len(branches)
    y_root = h / 2
    tot2 = sum(len(b[2]) for b in branches)
    ys = [30 + (h - 60) * (i + 0.5) / tot2 for i in range(tot2)]
    k = 0
    out.append(f"<circle cx='{x0}' cy='{y_root}' r='4' fill='{NUIT}'/>")
    for lab1, p1, subs in branches:
        idx = list(range(k, k + len(subs)))
        y1 = sum(ys[i] for i in idx) / len(idx)
        out.append(f"<line x1='{x0}' y1='{y_root}' x2='{x1}' y2='{y1:.1f}' stroke='{NUIT}' stroke-width='1.6'/>")
        out.append(txt((x0 + x1) / 2 - 10, (y_root + y1) / 2 - 6, p1, 12, color=ROUGE, weight="bold"))
        out.append(txt(x1 + 8, y1 + 4, lab1, 13, "start", weight="bold"))
        for (lab2, p2), i in zip(subs, idx):
            out.append(f"<line x1='{x1 + 78}' y1='{y1:.1f}' x2='{x2}' y2='{ys[i]:.1f}' stroke='{NUIT}' stroke-width='1.6'/>")
            out.append(txt((x1 + 78 + x2) / 2, (y1 + ys[i]) / 2 - 6, p2, 12, color=ROUGE, weight="bold"))
            out.append(txt(x2 + 8, ys[i] + 4, lab2, 13, "start"))
        k += len(subs)
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ circuits électriques

def _res(x, y, horiz=True, label=""):
    if horiz:
        s = f"<rect x='{x - 22}' y='{y - 8}' width='44' height='16' fill='#fff' stroke='{NUIT}' stroke-width='1.8'/>" + txt(x, y - 13, label, 12)
    else:
        s = f"<rect x='{x - 8}' y='{y - 22}' width='16' height='44' fill='#fff' stroke='{NUIT}' stroke-width='1.8'/>" + txt(x + 14, y + 4, label, 12, "start")
    return s


def _meter(x, y, letter, label=""):
    return (f"<circle cx='{x}' cy='{y}' r='13' fill='#fff' stroke='{NUIT}' stroke-width='1.8'/>" + txt(x, y + 5, letter, 13, weight="bold")
            + (txt(x, y - 18, label, 12) if label else ""))


def _battery(x, y, label="", horiz=True):
    if horiz:
        return (f"<line x1='{x - 4}' y1='{y - 14}' x2='{x - 4}' y2='{y + 14}' stroke='{NUIT}' stroke-width='3'/>"
                f"<line x1='{x + 4}' y1='{y - 8}' x2='{x + 4}' y2='{y + 8}' stroke='{NUIT}' stroke-width='1.6'/>" + txt(x, y - 20, label, 12)
                + txt(x - 12, y + 26, "+", 13, weight="bold") + txt(x + 12, y + 26, "−", 13, weight="bold"))
    return (f"<line x1='{x - 14}' y1='{y - 4}' x2='{x + 14}' y2='{y - 4}' stroke='{NUIT}' stroke-width='3'/>"
            f"<line x1='{x - 8}' y1='{y + 4}' x2='{x + 8}' y2='{y + 4}' stroke='{NUIT}' stroke-width='1.6'/>" + txt(x - 20, y + 4, label, 12, "end")
            + txt(x + 20, y - 4, "+", 13, weight="bold") + txt(x + 20, y + 12, "−", 13, weight="bold"))


def _coil(x, y, label=""):
    arcs = "".join(f"<path d='M{x - 22 + 11 * i},{y} a5.5,6 0 0 1 11,0' fill='none' stroke='{NUIT}' stroke-width='1.8'/>" for i in range(4))
    return arcs + txt(x, y - 13, label, 12)


def _cap(x, y, label=""):
    return (f"<line x1='{x - 4}' y1='{y - 12}' x2='{x - 4}' y2='{y + 12}' stroke='{NUIT}' stroke-width='2.4'/>"
            f"<line x1='{x + 4}' y1='{y - 12}' x2='{x + 4}' y2='{y + 12}' stroke='{NUIT}' stroke-width='2.4'/>"
            f"<rect x='{x - 4}' y='{y - 12}' width='8' height='24' fill='#fff' stroke='none'/>"
            f"<line x1='{x - 4}' y1='{y - 12}' x2='{x - 4}' y2='{y + 12}' stroke='{NUIT}' stroke-width='2.4'/>"
            f"<line x1='{x + 4}' y1='{y - 12}' x2='{x + 4}' y2='{y + 12}' stroke='{NUIT}' stroke-width='2.4'/>" + txt(x, y - 17, label, 12))


def _lamp(x, y, label=""):
    return (f"<circle cx='{x}' cy='{y}' r='11' fill='#fff' stroke='{NUIT}' stroke-width='1.8'/>"
            f"<line x1='{x - 8}' y1='{y - 8}' x2='{x + 8}' y2='{y + 8}' stroke='{NUIT}' stroke-width='1.6'/>"
            f"<line x1='{x - 8}' y1='{y + 8}' x2='{x + 8}' y2='{y - 8}' stroke='{NUIT}' stroke-width='1.6'/>" + txt(x, y - 16, label, 12))


def circuit_serie(top: Sequence[tuple], source: tuple = ("U = 12 V",), bottom: Sequence[tuple] = (), w=460, h=236, ac=False) -> str:
    """Boucle rectangulaire : composants du haut (gauche→droite), source à gauche, composants du bas (droite→gauche).
    Composant : (type, label) avec type ∈ R, L, C, A, V, lampe."""
    L, R_, T, B = 60, w - 60, 50, h - 50
    out = [f"<rect x='{L}' y='{T}' width='{R_ - L}' height='{B - T}' fill='none' stroke='{NUIT}' stroke-width='1.8'/>"]
    draw = {"R": lambda x, y, l: _res(x, y, True, l), "L": _coil, "C": _cap, "A": lambda x, y, l: _meter(x, y, "A", l),
            "V": lambda x, y, l: _meter(x, y, "V", l), "lampe": _lamp}
    for i, (t, lab) in enumerate(top):
        x = L + (R_ - L) * (i + 1) / (len(top) + 1)
        out.append(f"<rect x='{x - 26}' y='{T - 16}' width='52' height='32' fill='#fff' stroke='none'/>")
        out.append(draw[t](x, T, lab))
    for i, (t, lab) in enumerate(bottom):
        x = R_ - (R_ - L) * (i + 1) / (len(bottom) + 1)
        out.append(f"<rect x='{x - 26}' y='{B - 16}' width='52' height='32' fill='#fff' stroke='none'/>")
        out.append(draw[t](x, B, lab))
    ym = (T + B) / 2
    out.append(f"<rect x='{L - 18}' y='{ym - 20}' width='36' height='40' fill='#fff' stroke='none'/>")
    if ac:
        out.append(f"<circle cx='{L}' cy='{ym}' r='14' fill='#fff' stroke='{NUIT}' stroke-width='1.8'/>"
                   f"<path d='M{L - 8},{ym} q4,-8 8,0 t8,0' fill='none' stroke='{NUIT}' stroke-width='1.6'/>" + txt(L + 70, B + 26, " ; ".join(source), 12, "middle"))
    else:
        out.append(_battery(L, ym, "", horiz=False) + txt(L + 70, B + 26, " ; ".join(source), 12, "middle"))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ optique : lentille convergente

def lentille(f: float, do: float, ho: float = 1.0, w=520, h=300, echelle=None) -> str:
    """Objet AB à la distance do (>0) d'une lentille convergente de distance focale f. Image calculée par conjugaison."""
    u = uid()
    di = 1 / (1 / f - 1 / do) if abs(do - f) > 1e-9 else None
    hi = -di / do * ho if di else None
    xs = [-do, 2 * f]
    if di:
        xs.append(di)
    span = max(abs(min(xs)), abs(max(xs))) * 1.15
    sc = echelle or (w / 2 - 30) / span
    cx, cy = w / 2, h / 2
    X = lambda x: cx + x * sc
    hsc = (h / 2 - 40) / max(ho, abs(hi) if hi else ho)
    Yv = lambda y: cy - y * hsc
    out = [f"<defs><marker id='fa{u}' markerWidth='8' markerHeight='8' refX='6' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='{ROUGE}'/></marker></defs>",
           f"<line x1='10' y1='{cy}' x2='{w - 10}' y2='{cy}' stroke='{ENCRE}' stroke-width='1.2'/>",
           f"<path d='M{cx},{cy - h / 2 + 20} L{cx - 7},{cy - h / 2 + 32} M{cx},{cy - h / 2 + 20} L{cx + 7},{cy - h / 2 + 32} M{cx},{cy + h / 2 - 20} L{cx - 7},{cy + h / 2 - 32} M{cx},{cy + h / 2 - 20} L{cx + 7},{cy + h / 2 - 32}' stroke='{NUIT}' stroke-width='2' fill='none'/>",
           f"<line x1='{cx}' y1='{cy - h / 2 + 20}' x2='{cx}' y2='{cy + h / 2 - 20}' stroke='{NUIT}' stroke-width='2.4'/>",
           txt(cx + 6, cy - h / 2 + 30, "L", 13, "start", weight="bold"), txt(cx + 4, cy + 16, "O", 12, "start")]
    for s, lab in ((-1, "F"), (1, "F'")):
        out.append(f"<line x1='{X(s * f)}' y1='{cy - 5}' x2='{X(s * f)}' y2='{cy + 5}' stroke='{NUIT}' stroke-width='2'/>")
        out.append(txt(X(s * f), cy + 20, lab, 13, weight="bold"))
    # objet
    out.append(f"<line x1='{X(-do)}' y1='{cy}' x2='{X(-do)}' y2='{Yv(ho)}' stroke='{NUIT}' stroke-width='2.6' marker-end='url(#fa{u})'/>")
    out.append(txt(X(-do), cy + 18, "A", 13, weight="bold"))
    out.append(txt(X(-do) - 8, Yv(ho) - 4, "B", 13, "end", weight="bold"))
    # rayons : parallèle -> F' ; par O
    if di:
        out.append(f"<line x1='{X(-do)}' y1='{Yv(ho)}' x2='{cx}' y2='{Yv(ho)}' stroke='{ROUGE}' stroke-width='1.4'/>")
        out.append(f"<line x1='{cx}' y1='{Yv(ho)}' x2='{X(di)}' y2='{Yv(hi)}' stroke='{ROUGE}' stroke-width='1.4'/>")
        out.append(f"<line x1='{X(-do)}' y1='{Yv(ho)}' x2='{X(di)}' y2='{Yv(hi)}' stroke='{ROUGE}' stroke-width='1.4'/>")
        out.append(f"<line x1='{X(di)}' y1='{cy}' x2='{X(di)}' y2='{Yv(hi)}' stroke='{VERT}' stroke-width='2.6' marker-end='url(#fa{u})'/>")
        out.append(txt(X(di), cy - 8 if hi < 0 else cy + 18, "A'", 13, weight="bold"))
        out.append(txt(X(di) + 8, Yv(hi) + 4, "B'", 13, "start", weight="bold"))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ mécanique : plan incliné et forces

def plan_incline(angle_deg: float, forces: Sequence[tuple], w=480, h=300, masse_label="m") -> str:
    """forces : (nom, angle en degrés dans le repère écran-math (0 = vers la droite, 90 = vers le haut), longueur px, couleur)."""
    u = uid()
    a = math.radians(angle_deg)
    L = 380
    x0, y0 = 50, h - 50
    x1, y1 = x0 + L, y0 - L * math.tan(a)
    out = [f"<defs><marker id='fr{u}' markerWidth='8' markerHeight='8' refX='6' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='{ROUGE}'/></marker></defs>",
           f"<polygon points='{x0},{y0} {x1},{y0} {x1},{y1:.1f}' fill='#F7F4EC' stroke='{NUIT}' stroke-width='1.8'/>",
           f"<path d='M{x0 + 70},{y0} A70,70 0 0 0 {x0 + 70 * math.cos(a):.1f},{y0 - 70 * math.sin(a):.1f}' fill='none' stroke='{ENCRE}' stroke-width='1.4'/>",
           txt(x0 + 88, y0 - 12, f"{fmt(angle_deg)}°", 13)]
    # bloc au milieu de la pente
    t = 0.5
    bx, by = x0 + t * (x1 - x0), y0 + t * (y1 - y0)
    s = 44
    nx, ny = -math.sin(a), -math.cos(a)  # normale sortante (écran : y vers le bas)
    tx, ty = math.cos(a), -math.sin(a)
    corners = [(bx + tx * s / 2, by + ty * s / 2), (bx - tx * s / 2, by - ty * s / 2),
               (bx - tx * s / 2 + nx * s, by - ty * s / 2 + ny * s), (bx + tx * s / 2 + nx * s, by + ty * s / 2 + ny * s)]
    out.append("<polygon points='" + " ".join(f"{x:.1f},{y:.1f}" for x, y in corners) + f"' fill='{NUIT}' fill-opacity='0.15' stroke='{NUIT}' stroke-width='1.8'/>")
    gx, gy = bx + nx * s / 2, by + ny * s / 2
    out.append(txt(gx, gy + 5, masse_label, 13, weight="bold"))
    for nom, ang, lon, col in forces:
        r = math.radians(ang)
        ex, ey = gx + lon * math.cos(r), gy - lon * math.sin(r)
        out.append(f"<line x1='{gx:.1f}' y1='{gy:.1f}' x2='{ex:.1f}' y2='{ey:.1f}' stroke='{col}' stroke-width='2.4' marker-end='url(#fr{u})'/>")
        out.append(txt(ex + 10 * math.cos(r), ey - 10 * math.sin(r) + 5, nom, 14, "middle", col, "bold"))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ échiquier de croisement

def punnett(gam_m: Sequence[str], gam_f: Sequence[str], cell: Callable[[str, str], str] | None = None, w_cell=74, titre_m="♂", titre_f="♀") -> str:
    cell = cell or (lambda a, b: "".join(sorted(a + b, key=lambda c: (c.lower(), c.islower()))))
    n, m = len(gam_m), len(gam_f)
    W, H = w_cell * (m + 1) + 2, w_cell * (n + 1) + 2
    out = [f"<rect x='1' y='1' width='{w_cell}' height='{w_cell}' fill='{NUIT}'/>", txt(1 + w_cell / 2, 1 + w_cell / 2 + 5, f"{titre_m} \\ {titre_f}", 13, color="#fff", weight="bold")]
    for j, g in enumerate(gam_f):
        x = 1 + w_cell * (j + 1)
        out.append(f"<rect x='{x}' y='1' width='{w_cell}' height='{w_cell}' fill='#F7F4EC' stroke='{GRILLE}'/>")
        out.append(txt(x + w_cell / 2, 1 + w_cell / 2 + 5, g, 15, weight="bold", color=NUIT))
    for i, gm in enumerate(gam_m):
        y = 1 + w_cell * (i + 1)
        out.append(f"<rect x='1' y='{y}' width='{w_cell}' height='{w_cell}' fill='#F7F4EC' stroke='{GRILLE}'/>")
        out.append(txt(1 + w_cell / 2, y + w_cell / 2 + 5, gm, 15, weight="bold", color=NUIT))
        for j, gf in enumerate(gam_f):
            x = 1 + w_cell * (j + 1)
            out.append(f"<rect x='{x}' y='{y}' width='{w_cell}' height='{w_cell}' fill='#fff' stroke='{GRILLE}'/>")
            out.append(txt(x + w_cell / 2, y + w_cell / 2 + 5, cell(gm, gf), 14))
    return svg(W, H, "".join(out))


# ------------------------------------------------------------------ arbre généalogique

def pedigree(gens: Sequence[Sequence[dict]], couples: Sequence[tuple], enfants: Sequence[tuple], w=520, h=300) -> str:
    """gens : listes de personnes par génération {id, sexe:'M'|'F', atteint:bool, label}. couples : (id1,id2). enfants : (id_couple_index, [ids])."""
    pos = {}
    out = []
    for gi, gen in enumerate(gens):
        y = 50 + gi * 95
        for pi, p in enumerate(gen):
            x = 60 + (w - 120) * (pi + 0.5) / len(gen)
            pos[p["id"]] = (x, y)
        out.append(txt(18, y + 5, ["I", "II", "III", "IV"][gi], 13, "start", weight="bold"))
    for a, b in couples:
        (xa, ya), (xb, yb) = pos[a], pos[b]
        out.append(f"<line x1='{xa}' y1='{ya}' x2='{xb}' y2='{yb}' stroke='{ENCRE}' stroke-width='1.6'/>")
    for ci, ids in enfants:
        a, b = couples[ci]
        (xa, ya), (xb, yb) = pos[a], pos[b]
        xm, ym = (xa + xb) / 2, ya
        ys = pos[ids[0]][1]
        out.append(f"<line x1='{xm}' y1='{ym}' x2='{xm}' y2='{ys - 40}' stroke='{ENCRE}' stroke-width='1.6'/>")
        xs = [pos[i][0] for i in ids]
        out.append(f"<line x1='{min(xs)}' y1='{ys - 40}' x2='{max(xs)}' y2='{ys - 40}' stroke='{ENCRE}' stroke-width='1.6'/>")
        for i in ids:
            out.append(f"<line x1='{pos[i][0]}' y1='{ys - 40}' x2='{pos[i][0]}' y2='{ys - 16}' stroke='{ENCRE}' stroke-width='1.6'/>")
    for gen in gens:
        for p in gen:
            x, y = pos[p["id"]]
            fill = NUIT if p.get("atteint") else "#fff"
            if p["sexe"] == "M":
                out.append(f"<rect x='{x - 15}' y='{y - 15}' width='30' height='30' fill='{fill}' stroke='{NUIT}' stroke-width='2'/>")
            else:
                out.append(f"<circle cx='{x}' cy='{y}' r='15' fill='{fill}' stroke='{NUIT}' stroke-width='2'/>")
            if p.get("porteur"):
                out.append(f"<circle cx='{x}' cy='{y}' r='5' fill='{NUIT}'/>")
            out.append(txt(x, y + 32, p.get("label", ""), 12))
            if p.get("q"):
                out.append(txt(x, y + 5, "?", 15, color=ROUGE, weight="bold"))
    out.append(f"<rect x='{w - 170}' y='{h - 58}' width='14' height='14' fill='{NUIT}'/>" + txt(w - 150, h - 46, "individu atteint", 12, "start"))
    out.append(f"<rect x='{w - 170}' y='{h - 34}' width='14' height='14' fill='#fff' stroke='{NUIT}' stroke-width='1.5'/>" + txt(w - 150, h - 22, "individu sain", 12, "start"))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ frise chronologique

def frise(evenements: Sequence[tuple], t0: float, t1: float, w=560, h=200, unite="", log=False, titre=None) -> str:
    out = []
    y = 110
    xa, xb = 40, w - 30
    X = (lambda t: xa + (xb - xa) * (math.log10(t) - math.log10(t0)) / (math.log10(t1) - math.log10(t0))) if log else (lambda t: xa + (xb - xa) * (t - t0) / (t1 - t0))
    out.append(f"<line x1='{xa}' y1='{y}' x2='{xb}' y2='{y}' stroke='{NUIT}' stroke-width='3'/>")
    if titre:
        out.append(txt(w / 2, 24, titre, 13, weight="bold"))
    if log:
        out.append(txt(w - 30, h - 12, "échelle non linéaire", 11, "end", GRIS, italic=True))
    for i, (lab, t, *rest) in enumerate(evenements):
        x = X(t)
        up = i % 2 == 0
        anc = "start" if i == 0 else ("end" if i == len(evenements) - 1 else "middle")
        out.append(f"<line x1='{x:.1f}' y1='{y - 8}' x2='{x:.1f}' y2='{y + 8}' stroke='{NUIT}' stroke-width='2'/>")
        out.append(txt(x, y + (-36 if up else 46), lab, 12, anc, weight="bold"))
        out.append(txt(x, y + (-20 if up else 30), (rest[0] if rest else fmt(t) + unite), 12, anc, color=GRIS))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ pavé en perspective cavalière

def pave(a: float, b: float, c: float, w=480, h=280, labels=("a", "b", "c")) -> str:
    sc = min(300 / (a + 0.5 * b), 60)
    x0, y0 = 60, h - 60
    ax, bx, cx = a * sc, b * sc * 0.5, c * sc  # b en fuyante à 45°, réduite de moitié
    P = {"A": (x0, y0), "B": (x0 + ax, y0), "C": (x0 + ax + bx, y0 - bx), "D": (x0 + bx, y0 - bx),
         "E": (x0, y0 - cx), "F": (x0 + ax, y0 - cx), "G": (x0 + ax + bx, y0 - bx - cx), "H": (x0 + bx, y0 - bx - cx)}
    L = lambda p, q, dash=False: f"<line x1='{P[p][0]:.1f}' y1='{P[p][1]:.1f}' x2='{P[q][0]:.1f}' y2='{P[q][1]:.1f}' stroke='{NUIT}' stroke-width='2'{' stroke-dasharray=\"5 4\"' if dash else ''}/>"
    out = [L("A", "B"), L("B", "C"), L("B", "F"), L("A", "E"), L("E", "F"), L("F", "G"), L("C", "G"), L("E", "H"), L("H", "G"),
           L("A", "D", True), L("D", "C", True), L("D", "H", True)]
    for k, (x, y) in P.items():
        dx, dy = (-10, 14) if k in "AB" else (10, 14) if k == "C" else (-10, -4) if k in "EH" else (10, -4)
        out.append(txt(x + dx, y + dy, k, 13, weight="bold"))
    out.append(txt((P["A"][0] + P["B"][0]) / 2, y0 + 22, labels[0], 13, color=ROUGE, weight="bold"))
    out.append(txt((P["B"][0] + P["C"][0]) / 2 + 22, (P["B"][1] + P["C"][1]) / 2 + 16, labels[1], 13, color=ROUGE, weight="bold", anchor="start"))
    out.append(txt(P["F"][0] + P["C"][0] - P["B"][0] + 14, (P["C"][1] + P["G"][1]) / 2 + 4, labels[2], 13, color=ROUGE, weight="bold", anchor="start"))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ diagramme de cases quantiques

def cases_quantiques(config: Sequence[tuple], w=460, h=150) -> str:
    """config : [(sous-couche, [occupation par case : 0,1,2]), ...]"""
    out = []
    x = 20
    for sc, cases in config:
        for occ in cases:
            out.append(f"<rect x='{x}' y='60' width='30' height='30' fill='#fff' stroke='{NUIT}' stroke-width='1.6'/>")
            if occ >= 1:
                out.append(f"<path d='M{x + 10},84 L{x + 10},66 M{x + 10},66 L{x + 6},72 M{x + 10},66 L{x + 14},72' stroke='{ENCRE}' stroke-width='1.6' fill='none'/>")
            if occ == 2:
                out.append(f"<path d='M{x + 20},66 L{x + 20},84 M{x + 20},84 L{x + 16},78 M{x + 20},84 L{x + 24},78' stroke='{ENCRE}' stroke-width='1.6' fill='none'/>")
            x += 32
        out.append(txt(x - 16 * len(cases) - 2, 112, sc, 13, weight="bold"))
        x += 22
    return svg(max(w, x + 10), h, "".join(out))


# ------------------------------------------------------------------ montage de titrage

def montage_titrage(numeros: bool = True, w=360, h=330) -> str:
    out = []
    # statif
    out.append(f"<rect x='40' y='300' width='140' height='8' fill='{NUIT}'/><rect x='60' y='40' width='6' height='262' fill='{NUIT}'/>")
    out.append(f"<rect x='66' y='70' width='70' height='6' fill='{NUIT}'/>")
    # burette
    out.append(f"<rect x='128' y='40' width='16' height='170' fill='#E8F1FA' stroke='{NUIT}' stroke-width='1.6'/>")
    for i in range(9):
        out.append(f"<line x1='128' y1='{60 + 16 * i}' x2='{134 if i % 2 else 138}' y2='{60 + 16 * i}' stroke='{NUIT}'/>")
    out.append(f"<rect x='128' y='40' width='16' height='60' fill='#fff' stroke='none'/><rect x='128' y='40' width='16' height='170' fill='none' stroke='{NUIT}' stroke-width='1.6'/>")
    out.append(f"<polygon points='128,210 144,210 138,224 134,224' fill='{NUIT}'/><rect x='131' y='224' width='10' height='14' fill='#fff' stroke='{NUIT}'/>")
    out.append(f"<rect x='122' y='214' width='28' height='6' fill='{OR}'/>")
    # erlenmeyer
    out.append(f"<path d='M118,246 L154,246 L154,262 L182,300 L90,300 L118,262 z' fill='#FBEFEF' stroke='{NUIT}' stroke-width='1.8'/>")
    out.append(f"<path d='M101,286 L171,286 L182,300 L90,300 z' fill='{ROUGE}' fill-opacity='0.35' stroke='none'/>")
    # agitateur
    out.append(f"<rect x='84' y='300' width='104' height='0' fill='none'/>")
    out.append(f"<rect x='80' y='304' width='112' height='22' rx='4' fill='#D9D4C7' stroke='{NUIT}'/><circle cx='176' cy='315' r='4' fill='{NUIT}'/>")
    out.append(f"<rect x='126' y='292' width='20' height='4' rx='2' fill='{NUIT}'/>")
    if numeros:
        for n, (x, y, lx, ly) in enumerate([(136, 120, 200, 120), (138, 220, 200, 226), (136, 280, 220, 272), (136, 315, 220, 318), (136, 294, 220, 296)], 1):
            out.append(f"<line x1='{x}' y1='{y}' x2='{lx - 14}' y2='{ly - 4}' stroke='{GRIS}' stroke-width='1'/>")
            out.append(f"<circle cx='{lx}' cy='{ly - 4}' r='11' fill='{NUIT}'/>" + txt(lx, ly, str(n), 12, color="#fff", weight="bold"))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ pile électrochimique

def pile(gauche=("Zn", "Zn²⁺"), droite=("Cu", "Cu²⁺"), w=480, h=260) -> str:
    out = []
    for i, (metal, ion, x) in enumerate([(gauche[0], gauche[1], 90), (droite[0], droite[1], 330)]):
        out.append(f"<path d='M{x - 50},110 L{x - 50},230 L{x + 50},230 L{x + 50},110' fill='#E8F1FA' stroke='{NUIT}' stroke-width='1.8'/>")
        out.append(f"<rect x='{x - 8}' y='60' width='16' height='150' fill='{'#9AA3AD' if i == 0 else '#C27A3D'}' stroke='{NUIT}'/>")
        out.append(txt(x + (-14 if i == 0 else 14), 50, f"lame de {metal}", 12, "end" if i == 0 else "start"))
        out.append(txt(x, 250, f"solution de {ion}", 12))
    # pont salin
    out.append(f"<path d='M120,140 L120,100 L300,100 L300,140' fill='none' stroke='{NUIT}' stroke-width='14'/>"
               f"<path d='M120,140 L120,100 L300,100 L300,140' fill='none' stroke='#F2E7C9' stroke-width='10'/>")
    out.append(txt(210, 92, "pont salin (KNO₃)", 12))
    # fils et voltmètre
    out.append(f"<path d='M90,60 L90,20 L330,20 L330,60' fill='none' stroke='{NUIT}' stroke-width='1.8'/>")
    out.append(f"<circle cx='210' cy='20' r='14' fill='#fff' stroke='{NUIT}' stroke-width='1.8'/>" + txt(210, 25, "V", 13, weight="bold"))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ corde vibrante (onde stationnaire)

def corde(n_ventres: int, longueur_label="L", w=520, h=180) -> str:
    out = []
    xa, xb, y = 50, w - 50, h / 2
    out.append(f"<rect x='{xa - 10}' y='{y - 50}' width='10' height='100' fill='{NUIT}'/><rect x='{xb}' y='{y - 50}' width='10' height='100' fill='{NUIT}'/>")
    for s in (1, -1):
        pts = []
        for i in range(201):
            x = xa + (xb - xa) * i / 200
            pts.append(f"{x:.1f},{y - s * 40 * math.sin(n_ventres * math.pi * i / 200):.1f}")
        out.append(f"<polyline fill='none' stroke='{NUIT if s == 1 else GRIS}' stroke-width='2.2' {'' if s == 1 else 'stroke-dasharray=\"5 4\"'} points='{' '.join(pts)}'/>")
    for k in range(n_ventres + 1):
        x = xa + (xb - xa) * k / n_ventres
        out.append(f"<circle cx='{x:.1f}' cy='{y}' r='4' fill='{ROUGE}'/>")
    out.append(f"<line x1='{xa}' y1='{y + 62}' x2='{xb}' y2='{y + 62}' stroke='{ENCRE}' stroke-width='1.2'/>")
    out.append(txt((xa + xb) / 2, y + 78, longueur_label, 13, weight="bold"))
    out.append(txt(xa + (xb - xa) / (2 * n_ventres), y - 48, "ventre", 11, color=GRIS) + txt(xa + (xb - xa) / n_ventres, y + 22, "nœud", 11, color=ROUGE))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ transformateur

def transformateur(n1: int, n2: int, u1: str, w=460, h=220) -> str:
    out = [f"<rect x='190' y='40' width='80' height='140' fill='none' stroke='{NUIT}' stroke-width='10'/>"]
    for i in range(6):
        out.append(f"<path d='M186,{70 + 14 * i} a8,7 0 0 0 0,14' fill='none' stroke='{OR}' stroke-width='3'/>")
    for i in range(3):
        out.append(f"<path d='M274,{90 + 14 * i} a8,7 0 0 1 0,14' fill='none' stroke='{OR}' stroke-width='3'/>")
    out.append(f"<path d='M186,70 L80,70 L80,154 L186,154' fill='none' stroke='{NUIT}' stroke-width='1.6'/>")
    out.append(f"<path d='M274,90 L380,90 L380,132 L274,132' fill='none' stroke='{NUIT}' stroke-width='1.6'/>")
    out.append(f"<circle cx='80' cy='112' r='14' fill='#fff' stroke='{NUIT}' stroke-width='1.8'/><path d='M72,112 q4,-8 8,0 t8,0' fill='none' stroke='{NUIT}' stroke-width='1.6'/>")
    out.append(txt(80, 140 + 24, f"U₁ = {u1}", 13, weight="bold"))
    out.append(_res(380, 111, False, ""))
    out.append(txt(380, 164, "U₂ = ?", 13, weight="bold", color=ROUGE))
    out.append(txt(130, 30, f"N₁ = {n1} spires", 13) + txt(340, 30, f"N₂ = {n2} spires", 13))
    out.append(txt(230, 200, "primaire                secondaire", 11, color=GRIS))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ chariots (choc)

def chariots(m1, v1, m2, v2, w=480, h=160) -> str:
    u = uid()
    out = [f"<defs><marker id='fc{u}' markerWidth='8' markerHeight='8' refX='6' refY='4' orient='auto'><path d='M0,0 L8,4 L0,8 z' fill='{ROUGE}'/></marker></defs>",
           f"<line x1='20' y1='120' x2='{w - 20}' y2='120' stroke='{NUIT}' stroke-width='3'/>"]
    for x, m, v, col in ((110, m1, v1, NUIT), (330, m2, v2, OR)):
        out.append(f"<rect x='{x - 50}' y='70' width='100' height='40' rx='4' fill='{col}' fill-opacity='0.2' stroke='{NUIT}' stroke-width='1.8'/>")
        out.append(f"<circle cx='{x - 30}' cy='115' r='7' fill='{NUIT}'/><circle cx='{x + 30}' cy='115' r='7' fill='{NUIT}'/>")
        out.append(txt(x, 95, f"m = {m}", 13, weight="bold"))
        if v:
            d = 1 if v > 0 else -1
            out.append(f"<line x1='{x}' y1='50' x2='{x + d * 60}' y2='50' stroke='{ROUGE}' stroke-width='2.4' marker-end='url(#fc{u})'/>")
            out.append(txt(x + d * 30, 40, f"v = {fmt(abs(v))} m/s", 12, color=ROUGE))
        else:
            out.append(txt(x, 46, "immobile", 12, color=GRIS))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ chromatogramme

def chromatogramme(depots: Sequence[tuple], front: float, w=440, h=320) -> str:
    """depots : (nom, [hauteurs des taches en cm]) ; front en cm. Échelle 1 cm = 24 px."""
    sc, base = 24, 280
    pw = w - 170
    out = [f"<rect x='60' y='20' width='{pw}' height='{base - 20 + 16}' fill='#FBF8F0' stroke='{NUIT}' stroke-width='1.6'/>",
           f"<line x1='60' y1='{base}' x2='{60 + pw}' y2='{base}' stroke='{NUIT}' stroke-dasharray='6 4'/>", txt(64 + pw, base + 4, "ligne de dépôt", 11, "start", GRIS),
           f"<line x1='60' y1='{base - front * sc:.1f}' x2='{60 + pw}' y2='{base - front * sc:.1f}' stroke='{ROUGE}' stroke-width='1.6'/>", txt(64 + pw, base - front * sc + 4, "front du solvant", 11, "start", ROUGE)]
    n = len(depots)
    for i, (nom, taches) in enumerate(depots):
        x = 60 + pw * (i + 0.5) / n
        out.append(f"<line x1='{x:.1f}' y1='{base - 4}' x2='{x:.1f}' y2='{base + 4}' stroke='{NUIT}' stroke-width='2'/>")
        out.append(txt(x, base + 26, nom, 12, weight="bold"))
        for hgt in taches:
            out.append(f"<ellipse cx='{x:.1f}' cy='{base - hgt * sc:.1f}' rx='9' ry='6' fill='{NUIT}' fill-opacity='0.75'/>")
    # règle
    out.append(f"<line x1='30' y1='{base}' x2='30' y2='{base - front * sc - 10:.1f}' stroke='{ENCRE}'/>")
    for k in range(int(front) + 1):
        out.append(f"<line x1='26' y1='{base - k * sc:.1f}' x2='34' y2='{base - k * sc:.1f}' stroke='{ENCRE}'/>")
        out.append(txt(22, base - k * sc + 4, str(k), 10, "end"))
    out.append(txt(30, 16, "cm", 10))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ pyramide écologique / réseau

def reseau_trophique(noeuds: Sequence[tuple], fleches: Sequence[tuple], w=520, h=300) -> str:
    """noeuds : (id, label, x, y) ; flèches : (de, vers) = « est mangé par »."""
    u = uid()
    pos = {i: (x, y) for i, _, x, y in noeuds}
    out = [f"<defs><marker id='ft{u}' markerWidth='9' markerHeight='9' refX='8' refY='4.5' orient='auto'><path d='M0,0 L9,4.5 L0,9 z' fill='{NUIT}'/></marker></defs>"]
    for a, b in fleches:
        (xa, ya), (xb, yb) = pos[a], pos[b]
        dx, dy = xb - xa, yb - ya
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        out.append(f"<line x1='{xa + ux * 58:.1f}' y1='{ya + uy * 18:.1f}' x2='{xb - ux * 62:.1f}' y2='{yb - uy * 22:.1f}' stroke='{NUIT}' stroke-width='1.6' marker-end='url(#ft{u})'/>")
    for i, lab, x, y in noeuds:
        out.append(f"<rect x='{x - 64}' y='{y - 16}' width='128' height='32' rx='8' fill='#F7F4EC' stroke='{NUIT}' stroke-width='1.6'/>")
        out.append(txt(x, y + 5, lab, 12.5, weight="bold"))
    return svg(w, h, "".join(out))


# ------------------------------------------------------------------ diagramme P-V

def cycle_pv(points: Sequence[tuple], w=440, h=320) -> str:
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    xs_, ys_ = 10 ** math.floor(math.log10(max(xs))), 10 ** math.floor(math.log10(max(ys)))
    pl = Plot(0, max(xs) * 1.2, 0, max(ys) * 1.25, w, h, ml=70, xstep=xs_, ystep=ys_, xlabel="V (m³)", ylabel="P (Pa)",
              xfmt=lambda v: fmt(round(v, 4)), yfmt=lambda v: f"{v:,.0f}".replace(",", " "))
    pl.polyline(points, close=True, fill=OR)
    pl.parts[-1] = pl.parts[-1].replace(f"fill='{OR}'", f"fill='{OR}' fill-opacity='0.25'")
    for k, (x, y) in enumerate(points):
        pl.point(x, y, "ABCD"[k], dx=8, dy=-8)
    return pl.render()
