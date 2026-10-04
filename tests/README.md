# Tests für SimpleWiki

Die Tests prüfen `../simplewiki.html` im echten Browser: Jeder Test baut
eine instrumentierte Kopie der Wiki, öffnet sie in Chromium und liest danach
den Bericht aus, den das Testskript in der Seite selbst ablegt.

## Ausführen

```bash
python3 tests/alle.py            # alles
python3 tests/alle.py fluss      # nur die Tests mit "fluss" im Namen
python3 tests/t_order.py         # einen einzelnen Test
```

Endcode 0 heißt: alles bestanden. Endcode 1 heißt: mindestens eine Prüfung
ist fehlgeschlagen – dann nennt die Ausgabe den Namen der Prüfung.

Zwei Abhängigkeiten: **python3** und **chromium** im Pfad.

## Wie die Tests arbeiten

| Datei | Wofür |
|---|---|
| `alle.py` | führt alle Tests nacheinander aus und sammelt die Zahlen |
| `_hilfe.py` | Chromium starten, Bericht auslesen, Gesamtzahl melden |
| `mkcopy.py` | baut die Testkopie: Testseiten in `localStorage`, optional Daten aus der Datei, Testskript vor `</body>` |

Alle Kopien, PDFs und Zwischenstände landen in `tests/_kopien/` und werden
nicht committet. Der Ordner lässt sich jederzeit löschen.

## Die Tests

| Datei | Deckt ab |
|---|---|
| `t_empty.py` | Leerzustand, wenn keine Seite existiert |
| `t_suite.py` | Grundfunktionen: Oberfläche, Suche, Editor, Dunkelmodus |
| `t_link4.py` | Verlinken: Dialog, Seite anlegen, Rückverweise |
| `t_dup.py` | Kopieren einer Seite, unabhängige Verknüpfungen |
| `t_dupen.py` | dasselbe in englischer Oberfläche |
| `t_wikisyn.py` | `[[Seite]]` und `[[Text\|Seite]]`, Code bleibt Code |
| `t_refs.py` | Verweis-Panel, Zähler, gespeicherter Zustand |
| `t_order.py` | Reihenfolge per Griff, Alt + Pfeil, Sperre bei der Suche |
| `t_file.py` | Wiki als Datei sichern und laden, fremde Datei |
| `t_export.py` | **die gesicherte Datei wirklich auf die Platte schreiben und öffnen** |
| `t_fluss.py` | Fluss, Suche darin, Druckansicht als PDF |
| `t_scroll.py` | Scrollen im Fluss bei kurzem Fenster, Druck über mehrere Seiten |

## Zwei Lehren aus den Tests

**Teste die Aufgabe, nicht die Umsetzung.** Beim Sichern stand einmal im
Test „Oberfläche leer im Ergebnis“ – das prüfte, dass die Datei kaputt ist.
Der Test war grün und die Funktion kaputt. `t_export.py` schreibt die
gesicherte Datei jetzt wirklich auf die Platte und öffnet sie neu.

**Teste mit dem Fenster, in dem es benutzt wird.** Der Fluss ließ sich nicht
scrollen und der Druck verlor alles nach Bildschirmhöhe. Beides fiel nur
auf, weil `t_scroll.py` mit einem Fenster von 900×420 Pixeln und absichtlich
langen Seiten prüft – und der letzte Satz der letzten Seite muss im
ausgelesenen PDF stehen, nicht nur „sieht vollständig aus“.

## Wenn ein Test ausfliegt

`tests/_kopien/` enthält die Kopie, mit der es schiefging. Der Bericht steht
im ausgedruckten HTML:

```bash
python3 tests/alle.py            # zeigt an, welcher Test und welche Prüfung
chromium --headless --dump-dom "file://$PWD/tests/_kopien/_order1.html"
```