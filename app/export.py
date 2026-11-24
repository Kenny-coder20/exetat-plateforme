"""Export d'une série : JSON et LaTeX (cahier des charges § 8)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "exports"

_TEX_ESC = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}", "\\": r"\textbackslash{}"}


def tex(s: str | None) -> str:
    if not s:
        return ""
    s = "".join(_TEX_ESC.get(c, c) for c in s)
    s = s.replace("Ω", r"\,$\Omega$").replace("×", r"$\times$").replace("−", r"$-$").replace("→", r"$\rightarrow$")
    s = s.replace("≤", r"$\leq$").replace("≥", r"$\geq$").replace("°", r"$^{\circ}$")
    return s


def exporter_json(serie: dict, nom: str) -> Path:
    EXPORTS.mkdir(exist_ok=True)
    p = EXPORTS / f"{nom}.json"
    p.write_text(json.dumps(serie, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def latex_serie(serie: dict, *, titre_epreuve: str, option: str = "1.02 Sciences", session: int = 2026,
                code_epreuve: str = "", serie_lettre: str = "A", duree: str = "", competences: list[str] | None = None) -> str:
    items = serie["items"]
    n = len(items)
    comp = competences or ["Calculer, modéliser et raisonner à partir d'une situation",
                           "Analyser et interpréter des données, un schéma ou un résultat",
                           "Transférer ses acquis à une situation nouvelle du quotidien congolais"]
    head = rf"""\documentclass[12pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[french]{{babel}}
\usepackage[margin=2.2cm]{{geometry}}
\usepackage{{amsmath,amssymb}}
\usepackage{{tikz,pgfplots}}
\pgfplotsset{{compat=1.18}}
\usepackage{{tcolorbox}}
\usepackage{{enumitem}}
\usepackage{{array,booktabs}}
\usepackage{{fancyhdr}}
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{EXETAT {session} --- {tex(titre_epreuve)}}}
\fancyhead[R]{{Série {serie_lettre}}}
\fancyfoot[C]{{\thepage}}
\setlength{{\parindent}}{{0pt}}
\begin{{document}}

\begin{{center}}
{{\Large\bfseries EXAMEN D'ÉTAT --- SESSION {session}}}\\[4pt]
{{\large Option {tex(option)} \quad Épreuve {tex(code_epreuve)} \quad Série {serie_lettre}}}\\[4pt]
{tex(titre_epreuve)} \quad --- \quad {n} questions \quad --- \quad Durée : {tex(duree)} \quad --- \quad 1 point par question, sans pénalité
\end{{center}}

\begin{{tcolorbox}}[title=Consignes]
Chaque question comporte cinq propositions numérotées de 1 à 5. Une seule est exacte. Reportez le numéro choisi sur la feuille de réponses. L'usage de la calculatrice est autorisé.
\end{{tcolorbox}}

\begin{{tcolorbox}}[title=Compétences évaluées]
\begin{{itemize}}[nosep]
{chr(10).join(r'\item ' + tex(c) for c in comp)}
\end{{itemize}}
\end{{tcolorbox}}

\section*{{Questions}}
"""
    corps = []
    disc_courante = None
    for it in items:
        d = it["discipline"] + (f" — {it['sous_discipline']}" if it.get("sous_discipline") else "")
        if d != disc_courante:
            corps.append(rf"\subsection*{{{tex(d)}}}")
            disc_courante = d
        corps.append(rf"\textbf{{Q{it['numero']}.}} \textit{{({tex(it['titre'])})}}\\" + "\n" + tex(it["tige"]) + "\n")
        if it.get("support_latex"):
            corps.append("\n\\begin{center}\n" + it["support_latex"] + "\n\\end{center}\n")
        props = " \\quad ".join(f"\\textbf{{{k}.}} {tex(it[f'p{k}'])}" for k in range(1, 6))
        corps.append("\n" + props + "\n\\vspace{6pt}\n")
    feuille = [r"\newpage\section*{Feuille de réponses}", r"\begin{center}\begin{tabular}{|c|c|c|c|c|c|}\hline",
               r"Question & 1 & 2 & 3 & 4 & 5 \\ \hline"]
    for it in items:
        feuille.append(rf"Q{it['numero']} & $\square$ & $\square$ & $\square$ & $\square$ & $\square$ \\ \hline")
    feuille.append(r"\end{tabular}\end{center}")
    corrige = [r"\newpage\section*{Corrigé détaillé}"]
    for it in items:
        corrige.append(rf"\textbf{{Q{it['numero']} --- Réponse : {it['reponse']}.}} " + tex(it["correction_detaillee"]))
        if it.get("erreurs_distracteurs"):
            corrige.append(r"\\ \textit{Erreurs visées : }" + tex(it["erreurs_distracteurs"]))
        corrige.append(r"\vspace{6pt}" + "\n")
    return head + "\n".join(corps) + "\n" + "\n".join(feuille) + "\n" + "\n".join(corrige) + "\n\\end{document}\n"


def exporter_latex(serie: dict, nom: str, **kw) -> Path:
    EXPORTS.mkdir(exist_ok=True)
    p = EXPORTS / f"{nom}.tex"
    p.write_text(latex_serie(serie, **kw), encoding="utf-8")
    return p


def compiler_pdf(tex_path: Path) -> Path | None:
    import shutil
    import subprocess

    if not shutil.which("pdflatex"):
        return None
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-output-directory", str(tex_path.parent),
                        str(tex_path)], capture_output=True)
    pdf = tex_path.with_suffix(".pdf")
    return pdf if pdf.exists() else None


def nom_fichier(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", s).strip("_")


def latex_situation(s: dict, *, session: int = 2026) -> str:
    qs = s["questions"]
    head = rf"""\documentclass[12pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}\usepackage[T1]{{fontenc}}\usepackage[french]{{babel}}
\usepackage[margin=2.2cm]{{geometry}}\usepackage{{amsmath,amssymb}}\usepackage{{tikz,pgfplots}}\pgfplotsset{{compat=1.18}}
\usepackage{{tcolorbox}}\usepackage{{enumitem}}\usepackage{{array,booktabs}}\usepackage{{fancyhdr}}
\pagestyle{{fancy}}\fancyhf{{}}\fancyhead[L]{{EXETAT {session} --- Exercice de synthèse}}\fancyhead[R]{{{tex(s['discipline'])}}}\fancyfoot[C]{{\thepage}}
\setlength{{\parindent}}{{0pt}}
\begin{{document}}
\begin{{center}}{{\Large\bfseries {tex(s['titre'])}}}\\[4pt]{{\large Exercice de synthèse --- {tex(s['discipline'])} --- {len(qs)} questions --- {s.get('duree_min') or 25} min}}\end{{center}}
\begin{{tcolorbox}}[title=Consignes]
Lisez la situation et les documents, puis répondez aux {len(qs)} questions. Chaque question comporte cinq propositions numérotées de 1 à 5 ; une seule est exacte. Chaque question peut être traitée indépendamment des autres. Calculatrice autorisée.
\end{{tcolorbox}}
\section*{{Situation}}
{tex(s['texte'])}
\begin{{tcolorbox}}[title=Documents]
{tex(s.get('document_texte'))}
"""
    if s.get("document_latex"):
        head += "\\\\[8pt]\n\\begin{center}\n" + s["document_latex"] + "\n\\end{center}\n"
    head += "\\end{tcolorbox}\n\\section*{Questions}\n"
    corps = []
    for q in qs:
        corps.append(rf"\textbf{{Q{q['numero']}.}} " + tex(q["tige"]) + "\n")
        corps.append("\n" + " \\quad ".join(f"\\textbf{{{k}.}} {tex(q[f'p{k}'])}" for k in range(1, 6)) + "\n\\vspace{6pt}\n")
    corrige = [r"\newpage\section*{Corrigé détaillé}"]
    for q in qs:
        corrige.append(rf"\textbf{{Q{q['numero']} --- Réponse : {q['reponse']}.}} " + tex(q["correction_detaillee"]))
        if q.get("erreurs_distracteurs"):
            corrige.append(r"\\ \textit{Erreurs visées : }" + tex(q["erreurs_distracteurs"]))
        corrige.append(r"\vspace{6pt}" + "\n")
    if s.get("synthese"):
        corrige.append("\\begin{tcolorbox}[title=Synthèse]\n" + tex(s["synthese"]) + "\n\\end{tcolorbox}\n")
    return head + "\n".join(corps) + "\n" + "\n".join(corrige) + "\n\\end{document}\n"


def exporter_situation_latex(s: dict, nom: str) -> Path:
    EXPORTS.mkdir(exist_ok=True)
    p = EXPORTS / f"{nom}.tex"
    p.write_text(latex_situation(s), encoding="utf-8")
    return p
