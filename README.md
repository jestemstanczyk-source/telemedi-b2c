# Telemedi B2C: kohorty i lejki

## Uruchomienie narzędzia

Wgraj folder `docs/` na GitHub Pages (Settings → Pages) albo przeciągnij go na **[app.netlify.com/drop](https://app.netlify.com/drop)** — link w 30 sekund, bez konta.

Działa też lokalnie: otwórz `docs/index.html` w przeglądarce (`python -m http.server` w tym katalogu albo po prostu double-click).

## Weryfikacja na pełnych danych

```bash
python pipeline/verify.py <ścieżka_do_csv> docs/index.html
```

Oblicza sumy z surowych CSV i porównuje z narzędziem. Oczekiwane: pacjenci 40 918, sesje 457 464, płatności OK 63 893, wydatki 1 017 307,31 zł, zamówienia 63 207.

## Odbudowa od zera

```bash
pip install pandas playwright && playwright install chromium
# Edytuj ścieżkę U= w pipeline/load.py na katalog z CSV
python pipeline/load.py && python pipeline/audit9.py && python pipeline/base.py && python pipeline/main_q.py
python pipeline/build_agg.py && python pipeline/build_delay.py && python pipeline/build_delay2.py
python pipeline/build_site.py
python pipeline/verify.py <csv_dir> docs/index.html
python pipeline/test.py   # headless Chromium, 8 zakładek
```

## Zawartość narzędzia (8 zakładek)

- **Czy to wzrost?** — odpowiedź na pytanie główne; dashboard zawyżał wzrost dzięki duplikatom i kontom QA; retencja przy równym wieku spada −6,5 pp
- **Kohorty** — dzienne; retencja A/B; rozkład skład vs zachowanie; heatmapa miesięczna
- **Lejek** — sesja → płatność; A/B per krok; z-score per segment; „różnica w zdarzeniach"
- **Wizyty i opóźnienia** — % spóźnień >20 min rano (0→40% od XI 2025); profil godzinowy A/B; retencja wg opóźnienia 1. wizyty; kontrola warstwowa; marża per specjalizacja × rabat; błąd iOS Safari/Chrome od 17.03.2026
- **Zdarzenia** — 9 wykrytych zdarzeń; klik ustawia okna A/B
- **Priorytety** — 9 pozycji z wartością, KPI i czasem wdrożenia
- **Czego nie wiemy** — 10 pytań nierozstrzygalnych
- **Dane i założenia** — kontrola sum (6 sprawdzeń), audyt DQ, 11 założeń

## Struktura repo

```
docs/               ← gotowe narzędzie (jeden plik HTML ~10 MB, no backend)
pipeline/           ← skrypty do budowania (load → clean → agg → build → verify)
exploration/        ← wszystkie skrypty eksploracji bez sprzątania
WORKLOG.md          ← ślad pracy: kroki, ślepe uliczki, poprawki
```
