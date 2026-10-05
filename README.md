# SimpleWiki

Ein Wiki, das **eine einzige Datei** ist.

`simplewiki.html` ist das ganze Programm: Oberfläche, Editor, Markdown,
Speicher und alle Bibliotheken stecken darin. Kein Server, kein Build, keine
Installation. Wer die Datei doppelklickt, hat ein Wiki; wer sie weiterreicht,
gibt ein Wiki weiter — mit dem Inhalt, den sein Ersteller darin abgelegt hat.

Das ist der ganze Gedanke. Alles Weitere ist Ausgestaltung davon.

---

## Loslegen

```bash
xdg-open simplewiki.html          # oder: im Dateimanager doppelklicken
```

Die erste Wiki bringt eine Startseite mit. Von dort aus: ☰ öffnet das
Inhaltsverzeichnis, „+ Neue Seite“ legt eine an, der Knopf unten rechts
schaltet den Editor ein.

Für die Tests:

```bash
python3 tests/alle.py             # alles
python3 tests/alle.py fluss       # nur die Tests mit "fluss" im Namen
python3 tests/t_order.py          # einen einzelnen Test
```

## Was drin ist

| | |
|---|---|
| **Schreiben** | Markdown, im WYSIWYG-Editor (TOAST UI) oder im reinen Textfeld |
| **Inhaltsverzeichnis** | als Menü links, beim Öffnen da, am Fähnchen zu- und aufklappbar |
| **Verlinken** | `[[Seite]]` und `[[Beschriftung\|Seite]]` im Text, dazu ein Dialog beim Bearbeiten |
| **Verweise** | Rück- und Ausgehende in einem eigenen Panel, mit Zähler im Kopf |
| **Reihenfolge** | per Ziehen oder mit Alt + Pfeiltaste; die Reihenfolge überlebt das Neuladen |
| **Duplizieren** | legt eine Kopie mit eigenem Namen an, ohne Verknüpfung zur Vorlage |
| **Suche** | im Kopf; filtert Inhaltsverzeichnis und Fluss |
| **Fluss** | alle Seiten hintereinander lesen und als PDF drucken |
| **Hell / Dunkel** | auch im Editor |
| **Sprache** | Deutsch und Englisch, fest eingebaut |
| **Austausch** | Wiki als Datei sichern und laden, JSON exportieren, leere Vorlage exportieren |

Eine Wiki besteht aus **Textseiten**. Es gibt keine Bilder: wer Inhalte mit
Bildern übergibt, verliert sie, und sollte das vorher sagen.

## Wie die Datei aufgebaut ist

`simplewiki.html` ist 4749 Zeilen lang und hat diese Teile, immer in derselben
Reihenfolge:

```
  1–181    zwei Kommentare im <head>: der Austauschvertrag und der
           MWS-Betrieb. Sie sind die eigentliche Dokumentation — hier steht,
           warum das Format so aussieht und was der Server liefern muss.
    182    <script id="simplewiki-daten">  die Dateninsel
 183–320   die eingebetteten Bibliotheken (Vue, marked, TOAST UI inkl. DOMPurify)
 321–1814  das Stylesheet
1827–2157  die Oberfläche (Vue-Template)
2159–4749  das Programm
```

Die beiden Kommentare im Kopf sind **normales HTML und kein Ballast**: wer die
Datei liest, liest dort zuerst den Vertrag. Zwei Dinge dort sind beim Ändern
besonders zu beachten:

- Der Austauschvertrag beschreibt den Aufbau der Dateninsel und was beim
  Einlesen passiert (unbekannte Felder bleiben, zu neue Dateien werden ganz
  abgelehnt, eine Datei ohne Seiten wird nicht übernommen).
- Der MWS-Abschnitt nennt den Punkt im Dokument, hinter dem der Server seine
  Tiddler einsetzt — **ohne den Punkt als Zeichenfolge zu zitieren**. MWS sucht
  wörtlich danach und nimmt den ersten Fundort im Dokument, auch einen in
  einem Kommentar. Ein zitierender Kommentar würde die Tiddler in sich hinein
  verschlucken: die Wiki stünde schön und leer da. Die Regel gilt ohne
  Ausnahme — der Text steht genau einmal in der Roh-Datei.

## Die zwei Betriebsarten

An **genau einer** Stelle im Programm steht, woher die Seiten kommen
(`simplewiki.html:2386`, „Wo die Seiten liegen: Browser oder MWS“):

- **Browser** — der Normalfall. Seiten liegen in `localStorage`. Eine per
  Doppelklick geöffnete Datei merkt sich genau so.
- **MWS** (MultiWikiServer) — ein Server, der SimpleWiki ausliefert, schreibt
  hinter den Punkt im Kopf Aufrufe von `$tw.preloadTiddler`, eines je Tiddler.
  Kommen Tiddler an, wird von dort gelesen und dorthin geschrieben.

Beide Speicher sprechen dieselben Methoden an (`laden`, `uebernehmen`,
`seiteSichern`, `seiteLoeschen`, `startseiteSetzen`, `themaSetzen`,
`spracheSetzen`, `status`, `abmelden`). Der Rest des Programms kennt den
Unterschied nicht. Steht der Punkt nicht da oder kommen keine Tiddler an,
bleibt alles im Browser.

Was SimpleWiki mit dem Server spricht:

| Aufruf | Wofür |
|---|---|
| `GET /recipe/<name>/status` | wer angemeldet ist und ob dieser Tab schreiben darf |
| `PUT /recipe/<name>/batch/list` | alle Tiddler holen |
| `PUT /recipe/<name>/batch/read` | bestimmte Tiddler holen |
| `PUT /recipe/<name>/batch/save` | schreiben |
| `PUT /recipe/<name>/batch/delete` | löschen |
| `POST /logout` | Sitzung löschen (Antwort 204) |
| `/login?redirect=/wiki/<name>` | Anmeldung — ein Link, weil sie Sache des Servers ist |

Alle Aufrufe mit dem Kopf `X-Requested-With: fetch`. Stapelaufrufe sind
**PUT, nicht POST**; so ist es in `RecipeRoutes.ts` des MWS festgeschrieben.

Vier Betriebszustände, alle am Server erkannt und nicht geraten:

- **niemand angemeldet** → „Nicht angemeldet“ als **Link** auf `/login`
  (mit dem Weg, von dem man kommt — wer in einer Wiki auf „Anmelden“ klickt,
  will danach wieder in dieser Wiki sein)
- **angemeldet, aber kein Schreibrecht** → Nur-Lesen-Hinweis, und die
  Schreibknöpfe sind **weg**, nicht nur grau
- **Sitzung läuft mitten drin ab** → die App merkt es beim nächsten
  Schreibversuch und schaltet ohne Neuladen um
- **Server antwortet gar nicht** → es wird nichts erfunden: kein
  Nur-Lesen-Zustand, keine verlorenen Schreibknöpfe. Ein Ausfall ist kein
  Rechteproblem.

## Das Austauschformat

Steckt in der Dateninsel und lässt sich als eigene `.json`-Datei schreiben und
lesen:

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

Drei Zusagen:

1. **JSON und HTML sind gleichwertig.** Beim Einlesen wird JSON versucht und
   nur akzeptiert, wenn ein `seiten`-Array drin ist; sonst greift der
   Datenblock der HTML-Datei.
2. **Fremde Felder bleiben.** `normiereSeiten` normalisiert die bekannten
   Felder und nimmt alles andere unverändert mit — ein Hin-und-Her-Weg über
   ein Werkzeug verliert nichts. Das gilt auf Seitenebene wie auf der
   obersten Ebene (`autor`, `herkunft`, `exportdatum` …).
3. **Zu neue Dateien werden ganz abgelehnt.** Fehlt `version` oder ist sie
   größer als die eigene, wird nichts übernommen und der Grund genannt.

Verknüpft wird über `title`, nicht über `id` — deshalb dürfen keine zwei
Seiten denselben Namen haben. Beim Anlegen wird ein vergebener Name still
eindeutig gemacht („Neue Seite 2“), beim Umbenennen wird abgelehnt und der
Name genannt: stilles Umbenennen beim Speichern wäre überraschend.

## Nach jeder Änderung provisionieren

**Die Wiki liest ihre Schelle aus dem Store, nicht aus dieser Datei.** Nach
einer Änderung an `simplewiki.html` ist deshalb ohne diesen Befehl alles
genau wie vorher — auch nach einem Neustart des Servers:

```bash
cd <MWS-Quellbaum>
npm start provision-simplewiki <pfad>/simplewiki.html
```

Der Befehl meldet `Template "SimpleWiki" updated`; danach muss der Browser
nur noch hart neu laden (Strg+Umschalt+R). Wer sich wundert, warum die eigene
Änderung nicht ankommt, hat fast immer diesen Schritt vergessen.

## Tests

Die Tests prüfen `simplewiki.html` im **echten Browser**: Jeder Test baut eine
instrumentierte Kopie der Wiki, öffnet sie in Chromium und liest danach den
Bericht aus, den das Testskript in der Seite selbst ablegt.

```bash
python3 tests/alle.py            # alles, Endecode 0 = alles bestanden
python3 tests/alle.py mws        # nur die Tests mit "mws" im Namen
python3 tests/t_fluss.py         # einen einzelnen Test
```

- **22 Testdateien**, 660 Prüfungen, rund 65 Browserläufe pro Suite-Lauf
  (die beiden Drucktests starten Chromium ein zweites Mal für das PDF).
- Ein Test steht **nicht** in `alle.py`, weil er einen echten Server startet:
  `tests/live_mws.py` prüft die Wiki gegen ein **echtes** MWS statt gegen die
  Testfigur aus `mwsserver.py`. Siehe `tests/README.md`.

Abhängigkeiten: **python3**, **chromium** im Pfad, und für die beiden
Drucktests zusätzlich **`pdfinfo`** und **`pdftotext`** (poppler-utils).

Es lohnt sich, `tests/README.md` zu lesen — dort stehen die Testdateien, was
der Testmechanismus genau tut, und zwei Lehren aus den Tests, die das
Programm geprägt haben:

> **Teste die Aufgabe, nicht die Umsetzung.** Beim Sichern stand einmal im
> Test „Oberfläche leer im Ergebnis“ — das prüfte, dass die Datei kaputt ist.
> Der Test war grün und die Funktion kaputt.
>
> **Teste mit dem Fenster, in dem es benutzt wird.** Der Fluss ließ sich nicht
> scrollen und der Druck verlor alles nach Bildschirmhöhe. Beides fiel nur auf,
> weil der Test mit einem Fenster von 900×420 Pixeln prüft.

## Mitgebrachte Bibliotheken

Alle fest eingebettet statt vom CDN geladen — eine strikte
Content-Security-Policy erlaubt nur `self`, und eine Wiki soll auch ohne Netz
laufen.

| Bibliothek | Version | Lizenz |
|---|---|---|
| Vue 3 | 3.5.43 | MIT |
| marked | 15.0.12 | MIT |
| TOAST UI Editor (inkl. DOMPurify 2.3.3) | 3.2.2 | MIT |

## Grenzen, die Absicht sind

- **Eine Datei, ein Nutzer.** Es gibt keine Serververwaltung, keine
  gleichzeitigen Bearbeiter, keine Rechteverwaltung im Wiki selbst — das
  kommt vom MWS, wenn es da ist.
- **Keine Bilder.** Siehe oben.
- **Kein Abgleich mit anderen Ansichten.** Der Endpunkt
  `/recipe/<name>/updates?since=<seq>` wird nicht aufgerufen, weil sein
  Antwortformat nicht festgelegt ist. Jede Änderung geht sofort raus, ein
  Neuladen zeigt den Stand des Servers.
- **Kein Login im Wiki.** MWS prüft das Passwort mit OPAQUE, und dafür lädt
  diese Wiki bewusst keine Plugins: sie holt ihre Seiten über `/recipe`. Es
  nachzubauen hieße, ein zweites Megabyte WebAssembly in jede Wiki-Seite zu
  legen. Abmelden geht von hier aus, weil es nichts zu beweisen gibt.

## Ordner

```
simplewiki.html      das ganze Wiki
tests/               Tests, Testhilfen, Testfiguren (siehe tests/README.md)
tests/_kopien/       Kopien, PDFs und Bilder der Testläufe – nicht committet
.gitignore
```