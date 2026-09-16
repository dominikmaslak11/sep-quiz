# -*- coding: utf-8 -*-
"""Scala banki czastkowe i eksportuje do pytania.json.

UWAGA: w plikach bank_*.py poprawna odpowiedz jest zawsze pierwsza na liscie —
tak sie je latwiej pisze i sprawdza. Przy eksporcie odpowiedzi sa TASOWANE
deterministycznie (staly seed), zeby w pliku JSON nie bylo widocznego wzorca.
"""
import json, random, sys, pathlib

KATALOG = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(KATALOG))

from zrodla import ZRODLA, DZIALY          # noqa: E402

SEED = 20260929   # data egzaminu — staly seed, zeby eksport byl powtarzalny


def zbierz():
    """Wczytuje KAZDY plik bank_*.py z katalogu projektu, ktory definiuje liste P.

    Dzieki temu dolozenie nowej partii pytan nie wymaga zmian w tym pliku.
    """
    import importlib
    pytania, zrodla = [], []
    for plik in sorted(KATALOG.glob("bank_*.py")):
        modul = importlib.import_module(plik.stem)
        if hasattr(modul, "P"):
            pytania.extend(modul.P)
            zrodla.append(f"{plik.stem} ({len(modul.P)})")
    print("  banki: " + ", ".join(zrodla))
    return pytania


def sprawdz(pytania):
    """Walidacja banku. Zwraca liste bledow (pusta = wszystko dobrze)."""
    bledy, widziane = [], set()
    nazwy_dzialow = {k for k, _ in DZIALY}
    for p in pytania:
        pid = p.get("id", "???")
        if pid in widziane:
            bledy.append(f"{pid}: zduplikowane id")
        widziane.add(pid)
        if len(p.get("odp", [])) != 4:
            bledy.append(f"{pid}: musi byc dokladnie 4 odpowiedzi")
        if len(set(p.get("odp", []))) != len(p.get("odp", [])):
            bledy.append(f"{pid}: powtorzone tresci odpowiedzi")
        if not 0 <= p.get("ok", -1) < 4:
            bledy.append(f"{pid}: zly indeks poprawnej odpowiedzi")
        if p.get("dzial") not in nazwy_dzialow:
            bledy.append(f"{pid}: nieznany dzial {p.get('dzial')!r}")
        if p.get("podstawa") not in ZRODLA:
            bledy.append(f"{pid}: nieznana podstawa {p.get('podstawa')!r}")
        if not p.get("wyj"):
            bledy.append(f"{pid}: brak wyjasnienia")
        if not set(p.get("zakres", [])) <= {"D", "E"}:
            bledy.append(f"{pid}: zakres moze zawierac tylko D i E")
    return bledy


def eksport():
    pytania = zbierz()
    bledy = sprawdz(pytania)
    if bledy:
        for b in bledy:
            print("BLAD:", b)
        raise SystemExit(1)

    rnd = random.Random(SEED)
    wyjscie = []
    for p in pytania:
        pary = list(enumerate(p["odp"]))
        rnd.shuffle(pary)
        nowe_odp = [t for _, t in pary]
        nowy_ok = next(i for i, (stary, _) in enumerate(pary) if stary == p["ok"])
        wyjscie.append({
            "id": p["id"], "dzial": p["dzial"], "zakres": p["zakres"],
            "pytanie": p["pytanie"], "odpowiedzi": nowe_odp, "poprawna": nowy_ok,
            "wyjasnienie": p["wyj"], "podstawa": p["podstawa"],
        })

    dane = {
        "wersja": "1.0",
        "opis": "Bank pytan do egzaminu kwalifikacyjnego URE grupy G1 (dozor D i eksploatacja E).",
        "dzialy": dict(DZIALY),
        "zrodla": ZRODLA,
        "pytania": wyjscie,
    }
    plik = KATALOG / "pytania.json"
    plik.write_text(json.dumps(dane, ensure_ascii=False, indent=2), encoding="utf-8")
    return plik, wyjscie


if __name__ == "__main__":
    plik, pyt = eksport()
    from collections import Counter
    print(f"Zapisano {plik} — {len(pyt)} pytan")
    for k, n in sorted(Counter(p["dzial"] for p in pyt).items(),
                       key=lambda x: [d for d, _ in DZIALY].index(x[0])):
        print(f"  {k:5s} {dict(DZIALY)[k][:44]:46s} {n:3d}")
    print(f"  tylko dozor (D): {sum(1 for p in pyt if p['zakres'] == ['D'])}")
