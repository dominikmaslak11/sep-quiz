# Quiz i egzaminy próbne SEP G1 (dozór D / eksploatacja E)

Narzędzie do przygotowania się do egzaminu kwalifikacyjnego URE dla grupy **G1**
(urządzenia, instalacje i sieci elektroenergetyczne do 1 kV i powyżej).

Powstało przed egzaminem **dozór G1 w dniu 29.09.2026**.

- **196 pytań** z odpowiedziami i wyjaśnieniami, w 10 działach
- **94 pytania oznaczone wyłącznie jako dozorowe** — organizacja pracy, polecenia, dokumentacja
- interaktywny **quiz w terminalu** z zapisem postępów i powtórką błędów
- generator **arkuszy egzaminacyjnych w PDF** wraz z kluczem odpowiedzi

---

## ⚖ Skąd pochodzą pytania

**Pytania są opracowaniem własnym na podstawie aktów normatywnych**, które w świetle
**art. 4 pkt 1 ustawy o prawie autorskim i prawach pokrewnych nie są przedmiotem prawa
autorskiego** — wolno je swobodnie cytować i przetwarzać.

Podstawą są w szczególności:

| skrót | akt |
|---|---|
| `BHP2019` | Rozporządzenie Ministra Energii z 28.08.2019 w sprawie BHP przy urządzeniach energetycznych (Dz.U. 2019 poz. 1830) |
| `KWAL2022` | Rozporządzenie MKiŚ z 1.07.2022 w sprawie zasad stwierdzania kwalifikacji (Dz.U. 2022 poz. 1392) |
| `PE` | Ustawa — Prawo energetyczne |
| `KP` | Kodeks pracy, dział X |
| `BHP1997` | Rozporządzenie MPiPS z 26.09.1997 w sprawie ogólnych przepisów BHP (Dz.U. 2003 nr 169 poz. 1650) |
| `ATEX` | Rozporządzenie Ministra Rozwoju z 06.06.2016 w sprawie urządzeń do atmosfer potencjalnie wybuchowych (Dz.U. 2016 poz. 817) |
| `PB` / `WT2002` | Prawo budowlane i warunki techniczne |
| `PN60364`, `PN61140`, `PN60529`, `PN62305` | normy przywołane opisowo |

Pełne teksty aktów: **https://isap.sejm.gov.pl** (bezpłatnie).

> ⚠ **Żadna treść nie pochodzi z komercyjnych podręczników ani zbiorów zadań.**
> Publikacje wydawnicze są chronione prawem autorskim, a egzemplarze elektroniczne
> bywają znakowane wodnie identyfikatorem kupującego — kopiowanie ich treści do
> publicznego repozytorium naraża osobę kupującą, nie wydawcę.
> Normy PN są chronione prawem autorskim i **przywołuje się je tu wyłącznie z nazwy**.

---

## Instalacja

Nic nie trzeba instalować poza Pythonem 3. Do składania PDF-ów potrzebny jest `xelatex`
z czcionką Carlito:

```bash
sudo apt install texlive-xetex fonts-crosextra-carlito
```

## Użycie

### Quiz w terminalu

```bash
python3 pytania.py                  # zbuduj pytania.json (raz, po każdej zmianie banku)

python3 quiz.py nauka               # wszystkie pytania, wyjaśnienie po każdym
python3 quiz.py nauka -z D -d I     # tylko dozór, tylko dział I
python3 quiz.py egzamin -n 25 -z D  # 25 losowych pytań, wynik na końcu
python3 quiz.py bledy               # powtórka tylko tego, co poszło źle
python3 quiz.py statystyki          # które pytania sprawiają najwięcej kłopotu
```

Postępy zapisują się w `postepy.json` (plik lokalny, poza repozytorium).

### Arkusze do wydruku

```bash
python3 egzamin_latex.py -n 25 -z D --wariantow 3
python3 egzamin_latex.py -d I,X --tytul "Powtórka: organizacja pracy i przepisy"
```

Wynik trafia do `egzaminy/`: arkusz z miejscem na podpis i wynik oraz osobny
**klucz odpowiedzi z wyjaśnieniami**.

## Działy

| | dział | pytań |
|---|---|---|
| I | Organizacja bezpiecznej pracy | 44 |
| II | Ochrona przeciwporażeniowa | 29 |
| III | Urządzenia w strefach zagrożonych wybuchem | 25 |
| IV | Prace kontrolno-pomiarowe do 1 kV | 21 |
| V | Zespoły prądotwórcze | 20 |
| VI | Pomoc przedlekarska | 15 |
| VII | Elektrotermia i elektroliza | 7 |
| VIII | Fotowoltaika i magazyny energii | 8 |
| IX | Trakcja elektryczna | 8 |
| X | Przepisy, kwalifikacje i dokumentacja | 19 |

## Jak dopisać własne pytania

Otwórz dowolny plik `bank_*.py` i dopisz wpis w tym samym formacie — albo załóż nowy
plik o nazwie zaczynającej się od `bank_`, bo `pytania.py` wykrywa banki automatycznie.
**Poprawna odpowiedź jest zawsze pierwsza na liście** — przy eksporcie odpowiedzi są
tasowane deterministycznie, więc w `pytania.json` nie widać wzorca. Potem:

```bash
python3 pytania.py     # waliduje bank i przebudowuje pytania.json
```

Walidacja sprawdza duplikaty identyfikatorów, liczbę odpowiedzi, poprawność działu
i podstawy prawnej oraz obecność wyjaśnienia.

## Aplikacja na Androida

W katalogu `android/` jest natywna aplikacja w Kotlinie. Czyta **ten sam `pytania.json`**
co wersja terminalowa — jedno źródło prawdy, więc nie da się rozjechać obu wersji.

| | |
|---|---|
| `minSdk` | **24** — działa od Androida 7 w górę |
| `targetSdk` / `compileSdk` | 34 |
| zależności | tylko `androidx.appcompat` — bez Compose, bez bibliotek sieciowych |
| uprawnienia | **żadne** — aplikacja działa w pełni offline |
| rozmiar | ok. 3 MB |

> ⚠ **`minSdk` celowo ustawiony nisko.** Telefon docelowy to Samsung M21 z Androidem 12 (API 31).
> Podnoszenie `minSdk` powyżej 31 odetnie to urządzenie — ten sam błąd wcześniej zablokował
> aktualizację innej aplikacji na tym telefonie.

### Budowanie

```bash
./zbuduj-apk.sh        # przebudowuje pytania.json, kopiuje do assets i składa APK
```

Wymaga Android SDK (`ANDROID_HOME`) i JDK 21. Gotowy plik: `SEP-Quiz-G1-v1.0.apk`.

### Instalacja na telefonie

**Najprościej:** pobierz gotowy plik APK z zakładki
[**Releases**](https://github.com/dominikmaslak11/sep-quiz/releases),
skopiuj na telefon i otwórz menedżerem plików.

Android poprosi o zgodę na instalację z nieznanego źródła — to normalne przy aplikacji
spoza sklepu Play. Aplikacja **nie prosi o żadne uprawnienia** i nie korzysta z sieci.

**Przez USB:**
```bash
adb install -r SEP-Quiz-G1-v1.0.0.apk
```

### Podpis wydania

Wydania są podpisane własnym certyfikatem, nie kluczem debugowym:

```
CN=Dominik Maslak, OU=SEP Quiz, O=Dominik Maslak, L=Kalisz, C=PL
SHA-256: f8:dc:b4:77:bf:6f:58:42:f6:eb:58:8b:bb:0d:c2:74:ef:5c:ac:3b:d3:8f:94:6d:2a:b6:67:1b:84:8b:e7:51
```

Odcisk można sprawdzić poleceniem:
```bash
apksigner verify --print-certs SEP-Quiz-G1-v1.0.0.apk
```

Plik keystore i hasło **nie znajdują się w repozytorium** — leżą poza nim i nie są publikowane.

### Co umie

- **Tryb nauki** — wyjaśnienie i podstawa prawna od razu po odpowiedzi
- **Egzamin próbny** — wynik i omówienie dopiero na końcu, próg 75%
- **Powtórka błędów** — wyłącznie pytania, które wcześniej poszły źle
- filtry: zakres D/E, dział, liczba pytań
- postępy i skuteczność zapisywane między uruchomieniami
- rozbicie błędów według działu, żeby było widać, czego się douczyć

## ⚠ Zastrzeżenie

Materiał pomocniczy do samodzielnej nauki. **Egzamin kwalifikacyjny URE ma formę ustną**,
więc test wielokrotnego wyboru ćwiczy znajomość faktów, ale nie umiejętność wytłumaczenia
procedury. Ucz się, mówiąc odpowiedzi na głos.

Autorzy nie ponoszą odpowiedzialności za wynik egzaminu ani za skutki zastosowania
zawartych tu informacji w praktyce.

## Licencja

MIT — patrz `LICENSE`.
