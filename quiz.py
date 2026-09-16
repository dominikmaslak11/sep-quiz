#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interaktywny quiz do egzaminu SEP G1 (dozor D / eksploatacja E).

Tryby:
  nauka    — natychmiastowa informacja zwrotna i wyjasnienie po kazdym pytaniu
  egzamin  — losowy zestaw, wynik i omowienie dopiero na koncu
  bledy    — powtorka wylacznie pytan, ktore wczesniej poszly zle

Postepy zapisywane sa w postepy.json obok skryptu.
"""
import argparse, json, pathlib, random, sys, datetime

KATALOG = pathlib.Path(__file__).resolve().parent
PLIK_PYTAN = KATALOG / "pytania.json"
PLIK_POSTEPOW = KATALOG / "postepy.json"

LITERY = "ABCD"
PROG_ZDANIA = 0.75          # 75% poprawnych = wynik pozytywny


class Kolory:
    OK, ZLE, INFO, TYT, SZARY, RESET, POGR = (
        "\033[92m", "\033[91m", "\033[96m", "\033[95m", "\033[90m", "\033[0m", "\033[1m")

    @classmethod
    def wylacz(cls):
        for a in ("OK", "ZLE", "INFO", "TYT", "SZARY", "RESET", "POGR"):
            setattr(cls, a, "")


def wczytaj_pytania():
    if not PLIK_PYTAN.exists():
        sys.exit(f"Brak {PLIK_PYTAN}. Uruchom najpierw:  python3 pytania.py")
    return json.loads(PLIK_PYTAN.read_text(encoding="utf-8"))


def wczytaj_postepy():
    if PLIK_POSTEPOW.exists():
        return json.loads(PLIK_POSTEPOW.read_text(encoding="utf-8"))
    return {"pytania": {}, "podejscia": []}


def zapisz_postepy(p):
    PLIK_POSTEPOW.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")


def filtruj(pytania, zakres=None, dzial=None):
    out = pytania
    if zakres:
        out = [p for p in out if zakres in p["zakres"]]
    if dzial:
        chce = {d.strip().upper() for d in dzial.split(",")}
        out = [p for p in out if p["dzial"] in chce]
    return out


def zadaj(p, dane, numer, ile, pokaz_od_razu):
    """Zadaje jedno pytanie. Zwraca (czy_poprawnie, indeks_odpowiedzi) lub (None, None) przy przerwaniu."""
    print(f"\n{Kolory.SZARY}[{numer}/{ile}]  dział {p['dzial']} · {dane['dzialy'][p['dzial']]}"
          f" · {'/'.join(p['zakres'])}  ({p['id']}){Kolory.RESET}")
    print(f"{Kolory.POGR}{p['pytanie']}{Kolory.RESET}\n")
    for i, o in enumerate(p["odpowiedzi"]):
        print(f"   {Kolory.INFO}{LITERY[i]}{Kolory.RESET}) {o}")

    while True:
        try:
            w = input(f"\n   Odpowiedź (A-D, q = koniec): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            return None, None
        if w in ("Q", "KONIEC"):
            return None, None
        if w in LITERY:
            wybor = LITERY.index(w)
            break
        print(f"   {Kolory.ZLE}Wpisz literę A, B, C lub D.{Kolory.RESET}")

    dobrze = wybor == p["poprawna"]
    if pokaz_od_razu:
        if dobrze:
            print(f"\n   {Kolory.OK}✓ Dobrze.{Kolory.RESET}")
        else:
            print(f"\n   {Kolory.ZLE}✗ Źle. Poprawna: "
                  f"{LITERY[p['poprawna']]}) {p['odpowiedzi'][p['poprawna']]}{Kolory.RESET}")
        print(f"   {Kolory.SZARY}{p['wyjasnienie']}{Kolory.RESET}")
        print(f"   {Kolory.SZARY}Podstawa: {dane['zrodla'][p['podstawa']]}{Kolory.RESET}")
    return dobrze, wybor


def podsumowanie(wyniki, dane, pokaz_omowienie):
    ile = len(wyniki)
    dobre = sum(1 for _, ok, _ in wyniki if ok)
    proc = dobre / ile if ile else 0
    print(f"\n{Kolory.TYT}{'═' * 66}{Kolory.RESET}")
    print(f"{Kolory.POGR}WYNIK: {dobre}/{ile}  ({proc:.0%}){Kolory.RESET}")
    if proc >= PROG_ZDANIA:
        print(f"{Kolory.OK}Powyżej progu {PROG_ZDANIA:.0%} — tak trzymaj.{Kolory.RESET}")
    else:
        print(f"{Kolory.ZLE}Poniżej progu {PROG_ZDANIA:.0%}.{Kolory.RESET}")

    zle = [(p, w) for p, ok, w in wyniki if not ok]
    if zle:
        # rozklad bledow wg dzialu — pokazuje, czego sie douczyc
        from collections import Counter
        licznik = Counter(p["dzial"] for p, _ in zle)
        print(f"\n{Kolory.POGR}Błędy według działu:{Kolory.RESET}")
        for d, n in licznik.most_common():
            print(f"   {d:5s} {dane['dzialy'][d][:42]:44s} {n}")

    if zle and pokaz_omowienie:
        print(f"\n{Kolory.TYT}{'─' * 66}\nOMÓWIENIE BŁĘDÓW\n{'─' * 66}{Kolory.RESET}")
        for p, wybor in zle:
            print(f"\n{Kolory.SZARY}{p['id']} · dział {p['dzial']}{Kolory.RESET}")
            print(f"{Kolory.POGR}{p['pytanie']}{Kolory.RESET}")
            print(f"   {Kolory.ZLE}Twoja: {LITERY[wybor]}) {p['odpowiedzi'][wybor]}{Kolory.RESET}")
            print(f"   {Kolory.OK}Poprawna: {LITERY[p['poprawna']]}) {p['odpowiedzi'][p['poprawna']]}{Kolory.RESET}")
            print(f"   {Kolory.SZARY}{p['wyjasnienie']}{Kolory.RESET}")
    return dobre, ile


def main():
    ap = argparse.ArgumentParser(description="Quiz SEP G1 — dozór i eksploatacja")
    ap.add_argument("tryb", nargs="?", default="nauka", choices=["nauka", "egzamin", "bledy", "statystyki"])
    ap.add_argument("-n", "--ile", type=int, default=0, help="ile pytań (0 = wszystkie)")
    ap.add_argument("-z", "--zakres", choices=["D", "E"], help="tylko pytania dla dozoru albo eksploatacji")
    ap.add_argument("-d", "--dzial", help="np. I lub I,II,X")
    ap.add_argument("--bez-kolorow", action="store_true")
    a = ap.parse_args()

    if a.bez_kolorow or not sys.stdout.isatty():
        Kolory.wylacz()

    dane = wczytaj_pytania()
    postepy = wczytaj_postepy()

    if a.tryb == "statystyki":
        st = postepy["pytania"]
        if not st:
            print("Brak zapisanych podejść. Uruchom najpierw quiz.")
            return
        print(f"{Kolory.POGR}Pytania, które sprawiają najwięcej kłopotu:{Kolory.RESET}\n")
        ranking = sorted(st.items(), key=lambda kv: (kv[1]["dobrze"] / max(kv[1]["razem"], 1), -kv[1]["razem"]))
        wg_id = {p["id"]: p for p in dane["pytania"]}
        for pid, s in ranking[:15]:
            if pid not in wg_id:
                continue
            print(f"  {pid:7s} {s['dobrze']}/{s['razem']}  {wg_id[pid]['pytanie'][:58]}")
        print(f"\nPodejść łącznie: {len(postepy['podejscia'])}")
        for pod in postepy["podejscia"][-5:]:
            print(f"  {pod['data'][:16]}  {pod['tryb']:8s} {pod['wynik']}/{pod['ile']}")
        return

    pytania = filtruj(dane["pytania"], a.zakres, a.dzial)

    if a.tryb == "bledy":
        slabe = {pid for pid, s in postepy["pytania"].items() if s["dobrze"] < s["razem"]}
        pytania = [p for p in pytania if p["id"] in slabe]
        if not pytania:
            print("Nie ma zapisanych błędów do powtórki. Zagraj w tryb nauka albo egzamin.")
            return

    if not pytania:
        sys.exit("Żadne pytanie nie pasuje do podanych filtrów.")

    random.shuffle(pytania)
    if a.ile and a.ile < len(pytania):
        pytania = pytania[: a.ile]

    naglowek = {"nauka": "TRYB NAUKI", "egzamin": "EGZAMIN PRÓBNY", "bledy": "POWTÓRKA BŁĘDÓW"}[a.tryb]
    print(f"\n{Kolory.TYT}{'═' * 66}")
    print(f"{naglowek} — {len(pytania)} pytań"
          + (f", zakres {a.zakres}" if a.zakres else "")
          + (f", dział {a.dzial}" if a.dzial else ""))
    print(f"{'═' * 66}{Kolory.RESET}")
    if a.tryb == "egzamin":
        print(f"{Kolory.SZARY}Odpowiedzi i omówienie dopiero na końcu. Próg: {PROG_ZDANIA:.0%}.{Kolory.RESET}")

    wyniki = []
    for i, p in enumerate(pytania, 1):
        ok, wybor = zadaj(p, dane, i, len(pytania), pokaz_od_razu=(a.tryb != "egzamin"))
        if ok is None:
            print(f"\n{Kolory.SZARY}Przerwano po {len(wyniki)} pytaniach.{Kolory.RESET}")
            break
        wyniki.append((p, ok, wybor))
        s = postepy["pytania"].setdefault(p["id"], {"razem": 0, "dobrze": 0})
        s["razem"] += 1
        s["dobrze"] += int(ok)

    if wyniki:
        dobre, ile = podsumowanie(wyniki, dane, pokaz_omowienie=True)
        postepy["podejscia"].append({
            "data": datetime.datetime.now().isoformat(timespec="seconds"),
            "tryb": a.tryb, "wynik": dobre, "ile": ile,
            "zakres": a.zakres or "wszystko", "dzial": a.dzial or "wszystkie",
        })
        zapisz_postepy(postepy)
        print(f"\n{Kolory.SZARY}Postępy zapisane w {PLIK_POSTEPOW.name}."
              f"  Powtórka błędów:  python3 quiz.py bledy{Kolory.RESET}")


if __name__ == "__main__":
    main()
