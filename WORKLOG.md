# Ślad pracy (chronologicznie, bez sprzątania)

Praca w czacie z Claude (Opus 5.5). Pełny eksport rozmowy jest częścią śladu; tu skrót kroków i błędów.

1. **Ładowanie** (`load.py`). Próba zapisu do parquet: brak pyarrow → przejście na pickle. UTC → Europe/Warsaw z obsługą zmiany czasu.
2. **Audyt sesji** (`audit1`). 0 duplikatów, pliki cięte po czasie PL (sesje z 22–24 UTC ostatniego dnia kwartału w następnym pliku, bez nakładania), visitor_id → maks. 1 konto.
3. **Audyt zdarzeń** (`audit2`). 0 duplikatów, 0 osieroconych, 0 złej kolejności. Zauważone: 65 278 sesji z płatnością za konsultację vs 65 882 zamówienia.
4. **Audyt zamówień** (`audit3`, `audit4`). Rozbieżność z p. 3 = 604 pełne duplikaty (10–24.06.2026). Kod TEST-QA: 22 konta wewnętrzne, 1 810 zamówień po 1 zł + 290 testowych zwrotów → usunięte całe konta.
5. **Spójność kwot** (`audit5`), **GO i powiązania** (`audit6`): czyste. Kontrola stref czasowych: created_at = payment_succeeded po konwersji, 0 s różnicy.
6. **Użytkownicy i wydatki** (`audit7`): bez braków dni; daty startu nowych kampanii.
7. **Luki trackingu** (`audit8`): stosunek sesji do kliknięć stały; spadki ruchu tylko w święta. Nie znaleziono luk.
8. **Tygodniowy lejek** (`audit9`): udział in-app 10% → 42%, konwersja 18–20% → 12%; niewyjaśniony skok 29.09.2025.
9. **Ścieżki** (`journey.py`). **BŁĄD**: `groupby().first()` w pandas pomija NaN kolumna po kolumnie, więc dla sesji direct brał UTM z kolejnej sesji. Tabela z tego kroku jest błędna (direct 5 485 zamiast 6 541). Wyłapane w `base.py` przez niezgodne liczby; poprawione na `head(1)`.
10. **Odtworzenie dashboardu** (`dash.py`): +51,9/+60,7/+50,3/+40,3% wychodzi dokładnie z surowych danych (z duplikatami, QA, brutto).
11. **Pytanie główne** (`main_q`, `mix`, `pnl`): wzrost nowych z dwóch kampanii social, retencja przy równym wieku spada, kontrybucja +27%, na zamówienie −19%.
12. **Kalendarz z danych** (`cal_scan.py`). **BŁĄD**: pierwotnie `calendar.py` przesłoniło moduł standardowy → pandas nie startował. Zmiana nazwy.
13. **Skaner punktów zmiany** (`cpscan.py`): iOS Safari 17.03.2026 (z=−20); potwierdzone w obrębie kanałów (`ios.py`).
14. **Awarie płatności** (`outage.py`): nie znalezione (ślepa uliczka, ale wynik).
15. **Skok 29.09.2025** (`logged.py`): koniec fali e-mail crm_go_upsell; zmiana składu.
16. **Statusy** (`status.py`): zwroty L4 z social 15,9% vs 5,5%.
17. **CAC** (`cac.py`). **BŁĄD**: KeyError, kolumna `utm_campaign` vs `campaign`; poprawione.
18. **Retencja starych kanałów vs iOS** (`ret_old.py`): spadek niezależny od iOS, prawdopodobnie sezonowość (niska pewność).
19. **Wycena** (`impact.py`, `prio.py`).
20. **Agregacja** (`build_agg.py`): pierwsza wersja z regionem w głównej kostce = za duża (>15 MB) → region osobno, lejek w dwóch kostkach. **POPRAWKA**: „powracający” liczony po dniu zamiast po momencie pierwszego zamówienia.
21. **Narzędzie**: rezygnacja z Chart.js (brak dostępu do CDN z kontenera, nie mogłem zweryfikować ścieżki) → własne wykresy SVG. **BŁĄD**: kolumna `n` nadpisana długością kostki w dekoderze → „K.n is not iterable”; poprawione na `len`.
22. **Przegląd wizualny** (zrzuty): wzrost zwrotów oznaczony na zielono, kolor serii = kolor zdarzeń, oś >100%, filtry zasłaniające treść na telefonie → poprawione. Werdykt przepisany po rozkładzie na poziomie kampanii (−5,0 pp skład, −1,5 pp zachowanie zamiast wcześniejszego „30/70” na poziomie kanałów).
## Dodatkowa sesja: weryfikacja niezależna + nowe znaleziska

### Co zweryfikowano niezależnie (6 punktów)
- v1_delay.py: opóźnienia internisty – nowe zdarzenie E8
- v2_ret.py: retencja vs opóźnienie – −12 pp po kontroli warstw (ślepa uliczka: statsmodels niedostępny, zastąpiony ważoną korektą MH)
- v3_noorder.py: 11 482 konta bez zakupu, 0 z nich dostało e-mail/SMS (nowe ustalenie)
- v4_ios.py: korekta E4 – −21 pp Safari, −13 pp Chrome, wyłącznie nowi pacjenci; hipoteza WebKit obalona
- v5_margin.py: 14 ujemnych kombinacji specjalizacja × rabat, suma −24 tys. zł
- v6_go.py: odnowienia 6,29% (dowolny czas), 4,30% w 60 dni – potwierdza poprzednią analizę

### Zmiany w narzędziu
- Nowa zakładka „Wizyty i opóźnienia" (rWizyty): wykres dzienny opóźnień rano vs reszta, profil godzinowy A/B, retencja wg opóźnienia 1. wizyty, kontrola warstwowa, marża, iOS before/after
- Próba dodania osobnej zakładki „Opóźnienia" – zduplikowała zawartość rWizyty → usunięta, treść zmergowana w rWizyty
- Zdarzenia E4 (iOS): zaktualizowane liczby (−21 pp Safari nowi, −13 pp Chrome nowi, in-app bez zmiany)
- Zdarzenie E8 dodane: narastające opóźnienia poranne od ~10.11.2025
- Priorytety przebudowane: iOS na #1 (70 tys. zł), obsada ranna #2 (56–70 tys. zł), CRM dla porzuconych kont jako nowy priorytet #4
- Dodano 3 nowe kostki do data.json: DL (opóźnienia dzień × pora), DL2 (kohorty × opóźnienie 1. wizyty), IOS (iOS sesje dzień × przeglądarka × nowy/powracający)

### Błędy i ślepe uliczki w tej sesji
- conflict: template.html miał zaawansowaną wersję z rWizyty (VD/VH/Q/M cubes) z poprzedniej sesji – nie byłem świadomy jej istnienia aż do inspekcji; duplikacja odkryta i usunięta
- enc() dla string columns w pandas 4.x: delay_g zapisana jako plain list zamiast dict/idx – obejście: DL2.delay_g dostępna jako tablica string, iterowana bezpośrednio w JS
- Plik calendar.py z pierwszej sesji nadal jest w exploration/ – nie usuwać (ślad pracy)
