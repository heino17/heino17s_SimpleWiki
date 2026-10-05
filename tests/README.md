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

## Nach jeder Änderung an `simplewiki.html` provisionieren

```bash
cd <MWS-Quellbaum>
npm start provision-simplewiki <pfad>/simplewiki.html
```

Die Wiki liest ihre Schale **aus dem Store**, nicht aus dieser Datei. Nach
einer Änderung an `simplewiki.html` ist deshalb ohne diesen Befehl alles
genau wie vorher — auch nach einem Neustart des Servers. Wer sich wundert,
warum die eigene Änderung nicht ankommt, hat fast immer diesen Schritt
vergessen; der Befehl meldet `Template "SimpleWiki" updated`, danach muss
der Browser nur noch hart neu laden (Strg+Umschalt+R).

Ein Test steht nicht in `alle.py`, weil er einen Server startet: `live_mws.py`
prüft die Wiki gegen ein **echtes** MWS statt gegen die Testfigur aus
`mwsserver.py`.

```bash
python3 tests/live_mws.py            # die Wiki wikiwise-booklet
python3 tests/live_mws.py mein-wiki  # eine andere
```

Er braucht ein gebautes `dist/mws.js` aus dem MWS-Quellbaum (dort
`npm run build`) und standardmäßig `dev/wiki` von dort. Er kopiert den
Dev-Store nach `tests/_kopien/live`, provisioniert die gebaute
`simplewiki.html` hinein, startet den Server auf einem freien Port,
sieht die Wiki in Chromium nach und räumt danach alles wieder weg. Der
Originalstore wird dabei nur gelesen. Liegt der MWS-Quellbaum woanders:
`MWS=/pfad/zum/mws python3 tests/live_mws.py`.

### Die Anmeldung live prüfen

Zusätzlich prüft er mit `MWS_USER` und `MWS_PASS` eine **echte Anmeldung**
am echten MWS — mit OPAQUE und der Bibliothek, die auch der MWS-Client
benutzt. Ohne die beiden wird dieser Teil übersprungen und nicht als
Fehler gezählt; der anonyme Lauf ist auch ohne Passwort vollständig.

```bash
MWS_USER=admin MWS_PASS=geheim python3 tests/live_mws.py
```

Ein Passwort gehört in die Umgebung und nicht in eine Datei. `MWS_PASS`
steht deshalb in keinem Test, keinem Skript und keinem Bericht.

Warum das überhaupt ein Node-Programm ist: der OPAQUE-Handshake gehört in
den Browser. Für einen Test mit Server braucht es aber keinen Browser,
sondern die Bibliothek — die wird hier geladen und über HTTP gesprochen.

## Wie die Tests arbeiten

| Datei | Wofür |
|---|---|
| `alle.py` | führt alle Tests nacheinander aus und sammelt die Zahlen |
| `_hilfe.py` | Chromium starten, Bericht auslesen, Gesamtzahl melden |
| `live_mws.py` | **Live-Check gegen ein echtes MWS** (nicht in `alle.py`, siehe oben) |
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
| `t_kopf.py` | Fluss-Knopf im Kopf: Umschalten, Reihenfolge, schmale Fenster |
| `t_order.py` | Reihenfolge per Griff, Alt + Pfeil, Sperre bei der Suche |
| `t_file.py` | Wiki als Datei sichern und laden, fremde Datei |
| `t_mws.py` | Austausch mit MWS: JSON, Versionsprüfung, fremde Felder, doppelte Titel |
| `t_anmeldung.py` | **Anmeldung und Schreibrechte: Statusabfrage, Name im Kopf, ausgeblendete Schreibknöpfe** |
| `t_login.py` | **Anmelden und abmelden: Link auf `/login`, `POST /logout`, der Fall, dass es nicht klappt** |
| `t_leerwiki.py` | Leere Wiki-Datei, Vorlage füllen und öffnen, Angaben oben |
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

## Last und Wiederholung

Das Einlesen einer Datei braucht echte Datei-Zeit, und die läuft nicht
mit der Uhr des Testskripts. Wenn mehrere Browser hintereinander laufen,
kommt es vor, dass ein Test beim ersten Lauf durchfällt, obwohl das Programm
in Ordnung ist. Deshalb läuft eine durchgefallene Kopie **einmal mit der
doppelten Zeit wieder** – erst ein zweimaliger Fehlschlag zählt als Fehler.
Solche Läufe sind in der Ausgabe als `(Wiederholung, …)` gekennzeichnet.

## Wenn ein Test ausfliegt

`tests/_kopien/` enthält die Kopie, mit der es schiefging. Der Bericht steht
im ausgedruckten HTML:

```bash
python3 tests/alle.py            # zeigt an, welcher Test und welche Prüfung
chromium --headless --dump-dom "file://$PWD/tests/_kopien/_order1.html"
```

## Austauschformat

SimpleWiki und MWS sprechen dasselbe Format. Es steckt im HTML in
`<script id="simplewiki-daten">` und lässt sich als eigene `.json`-Datei
schreiben und lesen:

```json
{
  "version": 1,
  "seiten": [
    {"id": "…", "title": "…", "content": "Markdown mit [[Verweisen]]",
     "links": ["Seitenname"], "tags": [], "created": "ISO-8601 mit Z",
     "updated": "ISO-8601 mit Z"}
  ],
  "startseite": "id der Startseite",
  "sprache": "de",
  "thema": "light"
}
```

Drei Zusagen, die `t_mws.py` prüft:

1. **JSON und HTML sind gleichwertig.** Beim Einlesen wird JSON versucht
   und nur akzeptiert, wenn ein `seiten`-Array drin ist; sonst greift der
   Datenblock der HTML-Datei.
2. **Fremde Felder bleiben.** `normiereSeiten` normalisiert die bekannten
   Felder und nimmt alles andere unverändert mit – ein Hin-und-Her-Weg
   über ein Werkzeug verliert nichts.
3. **Zu neue Dateien werden ganz abgelehnt.** Fehlt `version` oder ist sie
   größer als die eigene, wird nichts übernommen und der Grund genannt.

Zwei Entscheidungen, die nicht in der Vorgabe standen (jeweils eine Zeile,
wenn es anders sein soll):

- Eine Datei **ohne Seiten** wird abgelehnt statt als leeres Wiki
  übernommen: sonst ersetzt ein missglückter Export die ganze Wiki.
- Beim **Anlegen** wird ein vergebener Name still eindeutig gemacht
  („Neue Seite 2“), beim **Umbenennen** wird abgelehnt und der Name genannt
  – stilles Umbenennen beim Speichern wäre überraschend.
