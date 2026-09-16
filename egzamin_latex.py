#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generuje arkusz egzaminu probnego w LaTeX-u (+ klucz odpowiedzi) i sklada go do PDF.

Przyklad:
    python3 egzamin_latex.py -n 30 -z D --wariantow 3
    python3 egzamin_latex.py -d I,X --tytul "Powtorka: organizacja pracy"
"""
import argparse, json, pathlib, random, subprocess, shutil, sys, datetime

KATALOG = pathlib.Path(__file__).resolve().parent
WYJSCIE = KATALOG / "egzaminy"
LITERY = "ABCD"

PREAMBULA = r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\usepackage{polyglossia}
\setdefaultlanguage{polish}
\usepackage[top=16mm,bottom=16mm,left=18mm,right=18mm]{geometry}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{multicol}
\usepackage{fancyhdr}
\setmainfont{Carlito}[BoldFont=Carlito Bold, ItalicFont=Carlito Italic, Ligatures=TeX]
\definecolor{akcent}{HTML}{1F3864}
\definecolor{szary}{HTML}{595959}
\setlength{\parindent}{0pt}
\pagestyle{fancy}\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\fancyhead[L]{\small\color{szary}%(naglowek)s}
\fancyhead[R]{\small\color{szary}%(wariant)s}
\fancyfoot[C]{\small\color{szary}\thepage}
\newcommand{\pyt}[2]{\vspace{2.2mm}\textbf{#1.}~#2\par\vspace{0.6mm}}
\begin{document}
"""

METRYKA = r"""
{\color{akcent}\Large\bfseries %(tytul)s}\par
\vspace{1mm}
{\color{szary}\small %(podtytul)s}\par
\vspace{2mm}{\color{akcent}\rule{\linewidth}{1pt}}\par
\vspace{3mm}
\begin{tabular}{@{}p{58mm}p{58mm}p{50mm}@{}}
Imię i nazwisko: \dotfill & Data: \dotfill & Wynik: \dotfill \\
\end{tabular}
\vspace{2mm}{\color{szary}\rule{\linewidth}{0.4pt}}\par
\vspace{2mm}
{\small\color{szary}Zaznacz jedną odpowiedź. Próg zaliczenia: %(prog)d\%% poprawnych, czyli %(min_pkt)d z %(ile)d.}\par
\vspace{2mm}
"""


def esc(t):
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                 ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
                 ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        t = t.replace(a, b)
    return t


def zbuduj_arkusz(pytania, dane, tytul, podtytul, naglowek, wariant, prog):
    ile = len(pytania)
    min_pkt = -(-ile * prog // 100)
    txt = PREAMBULA % {"naglowek": esc(naglowek), "wariant": esc(wariant)}
    txt += METRYKA % {"tytul": esc(tytul), "podtytul": esc(podtytul),
                      "prog": prog, "min_pkt": min_pkt, "ile": ile}
    for i, p in enumerate(pytania, 1):
        txt += "\\pyt{%d}{%s}\n" % (i, esc(p["pytanie"]))
        txt += "\\begin{enumerate}[label=\\Alph*), leftmargin=9mm, topsep=0.4mm, itemsep=0.4mm]\n"
        for o in p["odpowiedzi"]:
            txt += "  \\item %s\n" % esc(o)
        txt += "\\end{enumerate}\n"
    txt += "\\end{document}\n"
    return txt


def zbuduj_klucz(pytania, dane, tytul, wariant):
    txt = PREAMBULA % {"naglowek": esc("KLUCZ ODPOWIEDZI — nie dawać zdającemu"),
                       "wariant": esc(wariant)}
    txt += r"{\color{akcent}\Large\bfseries KLUCZ: %s}\par\vspace{2mm}" % esc(tytul)
    txt += r"{\color{akcent}\rule{\linewidth}{1pt}}\par\vspace{3mm}" + "\n"
    txt += "\\begin{multicols}{2}\n"
    for i, p in enumerate(pytania, 1):
        txt += "\\textbf{%d. %s} {\\small\\color{szary}(%s, dz. %s)}\\par\n" % (
            i, LITERY[p["poprawna"]], esc(p["id"]), esc(p["dzial"]))
        txt += "{\\footnotesize %s\\par}\\vspace{1.4mm}\n" % esc(p["wyjasnienie"])
    txt += "\\end{multicols}\n"
    txt += r"\vspace{3mm}{\color{szary}\rule{\linewidth}{0.4pt}}\par\vspace{1.5mm}" + "\n"
    txt += "{\\footnotesize\\color{szary}Pytania opracowane na podstawie aktów normatywnych "
    txt += "(art. 4 pkt 1 ustawy o prawie autorskim — akty normatywne nie są przedmiotem prawa autorskiego).\\par}\n"
    txt += "\\end{document}\n"
    return txt


def skompiluj(tex_path):
    if not shutil.which("xelatex"):
        print("  (brak xelatex — zostawiam sam plik .tex)")
        return None
    subprocess.run(["xelatex", "-interaction=nonstopmode", tex_path.name],
                   cwd=tex_path.parent, capture_output=True)
    pdf = tex_path.with_suffix(".pdf")
    for ext in (".aux", ".log", ".out"):
        tex_path.with_suffix(ext).unlink(missing_ok=True)
    return pdf if pdf.exists() else None


def main():
    ap = argparse.ArgumentParser(description="Generator arkuszy egzaminacyjnych SEP G1")
    ap.add_argument("-n", "--ile", type=int, default=25)
    ap.add_argument("-z", "--zakres", choices=["D", "E"])
    ap.add_argument("-d", "--dzial")
    ap.add_argument("-w", "--wariantow", type=int, default=1, help="ile różnych zestawów wygenerować")
    ap.add_argument("--tytul", default="Egzamin próbny SEP — grupa G1")
    ap.add_argument("--prog", type=int, default=75)
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()

    plik = KATALOG / "pytania.json"
    if not plik.exists():
        sys.exit("Brak pytania.json — uruchom najpierw: python3 pytania.py")
    dane = json.loads(plik.read_text(encoding="utf-8"))

    pula = dane["pytania"]
    if a.zakres:
        pula = [p for p in pula if a.zakres in p["zakres"]]
    if a.dzial:
        chce = {d.strip().upper() for d in a.dzial.split(",")}
        pula = [p for p in pula if p["dzial"] in chce]
    if not pula:
        sys.exit("Żadne pytanie nie pasuje do filtrów.")
    if a.ile > len(pula):
        print(f"Uwaga: w puli jest tylko {len(pula)} pytań — tyle trafi do arkusza.")
        a.ile = len(pula)

    WYJSCIE.mkdir(exist_ok=True)
    rnd = random.Random(a.seed)
    dzis = datetime.date.today().strftime("%d.%m.%Y")
    opis_zakres = {"D": "dozór (D)", "E": "eksploatacja (E)"}.get(a.zakres, "dozór i eksploatacja")
    podtytul = f"{opis_zakres} · {a.ile} pytań · wygenerowano {dzis}"

    for w in range(1, a.wariantow + 1):
        wybrane = rnd.sample(pula, a.ile)
        wariant = f"wariant {w}" if a.wariantow > 1 else "arkusz"
        baza = f"egzamin_{a.zakres or 'DE'}_{a.ile}p_w{w}"

        tex = WYJSCIE / f"{baza}.tex"
        tex.write_text(zbuduj_arkusz(wybrane, dane, a.tytul, podtytul,
                                     a.tytul, wariant, a.prog), encoding="utf-8")
        pdf = skompiluj(tex)
        print(f"  {'✓' if pdf else '·'} {tex.name}" + (f"  →  {pdf.name}" if pdf else ""))

        ktex = WYJSCIE / f"{baza}_KLUCZ.tex"
        ktex.write_text(zbuduj_klucz(wybrane, dane, a.tytul, wariant), encoding="utf-8")
        kpdf = skompiluj(ktex)
        print(f"  {'✓' if kpdf else '·'} {ktex.name}" + (f"  →  {kpdf.name}" if kpdf else ""))


if __name__ == "__main__":
    main()
