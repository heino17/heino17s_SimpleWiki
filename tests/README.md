# Tests für SimpleWiki

Die Tests prüfen `../simplewiki.html` im echten Browser: Jeder Test baut
eine instrumentierte Kopie der Wiki, öffnet sie in Chromium und liest danach
den Bericht aus, den das Testskript in der Seite selbst ablegt.

## Ausführen

```bash
python3 tests/alle.py            # alles, mehrere Tests gleichzeitig
python3 tests/alle.py fluss      # nur die Tests mit "fluss" im Namen
python3 tests/alle.py -j 1       # nacheinander
python3 tests/t_order.py         # einen einzelnen Test
```

Endcode 0 heißt: alles bestanden. Endcode 1 heißt: mindestens eine Prüfung
ist fehlgeschlagen – dann nennt die Ausgabe den Namen der Prüfung.

`alle.py` lässt die Dateien **gleichzeitig** laufen. Jeder Test ist ein eigener
Prozess mit eigener Kopie der Wiki und eigenem Browserfenster, sie stören sich
also nicht. Die Voreinstellung ist die Zahl der Prozessoren (höchstens acht);
`-j N` stellt sie ein, `-j 1` ist der alte Lauf nacheinander. Der Bericht steht
trotzdem in fester Reihenfolge da, damit zwei Läufe vergleichbar bleiben – oben
stehen nur die Fortschrittszeilen mit der Dauer je Datei.

Grundabhängigkeiten: **python3** und **chromium** im Pfad. Für die beiden
Drucktests kommen **`pdfinfo`** und **`pdftotext`** dazu (poppler-utils) — sie
lesen das erzeugte PDF aus und sagen, was wirklich drinsteht.

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

## Die Buchhaltung

Dieselben Zahlen stehen an mehreren Orten: die Fassung in der `<meta>`-Zeile
von `simplewiki.html`, in `README.md` und im Kopf des CHANGELOG, die
Prüfungszahl in der obersten CHANGELOG-Überschrift, Testdateien und Prüfungen
in `README.md` und `AGENTS.md`, dazu die Strukturtafel mit Länge und
Zeilenspannen. `buchhaltung.py` stellt sie an einer Stelle her.

```bash
python3 tests/alle.py                  # erst grün werden
python3 tests/buchhaltung.py           # dann buchhalten
python3 tests/buchhaltung.py --check   # nur melden (Endcode 1 = veraltet)
```

Die Fassung kommt aus der obersten `### vX.Y.Z`-Überschrift des CHANGELOG: wer
eine neue will, schreibt sie dort samt Beschreibung hin, das Skript trägt sie
in die drei `<meta>`-Zeilen. Die Prüfungszahl kommt aus dem letzten **vollen**
Durchgang, den `alle.py` in `tests/_kopien/letzter_lauf.json` ablegt; ohne
letzten Lauf hilft `--pruefungen N`. Ein gefilterter Lauf schreibt keinen
Bericht. Die Zeilenspannen liest das Skript aus `simplewiki.html` selbst — es
zählt nichts von Hand.

`t_buchhaltung.py` liest dieselben Quellen und meldet, was nicht mehr
zusammenpasst. Er braucht keinen Browser und keinen letzten Lauf, steht aber
in `alle.py` und ist damit Teil jeder Suite. Die Prüfungszahl selbst prüft er
nicht: sie steht erst nach einem vollen Durchgang fest.

Ein Test steht nicht in `alle.py`, weil er einen **echten** Server startet:
`live_mws.py` prüft die Wiki gegen ein **echtes** MWS statt gegen die Testfigur
aus `mwsserver.py`. Sechs weitere Tests starten zwar auch einen Server — aber den
kleinen aus `mwsserver.py`, und genau deshalb gehören sie in `alle.py`.

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
| `mkcopy.py` | baut die Testkopie: Testseiten in `localStorage`, optional Daten aus der Datei, Testskript vor `</body>` |
| `mwsserver.py` | der Testserver: Routen, Rechte, Sitzung, Fehler auf Kommando |
| `mwsfixture.py` | baut eine **Datei**, die so aussieht, als käme sie vom MWS |
| `live_mws.py` | **Live-Check gegen ein echtes MWS** (nicht in `alle.py`, siehe oben) |
| `buchhaltung.py` | stellt die wiederkehrenden Zahlen her (Fassung, Prüfungszahl, Strukturtafel), siehe unten |

Alle Kopien, PDFs und Zwischenstände landen in `tests/_kopien/` und werden
nicht committet. Der Ordner lässt sich jederzeit löschen.

## Die Tests

| Datei | Deckt ab |
|---|---|
| `t_empty.py` | Leerzustand, wenn keine Seite existiert |
| `t_suite.py` | Grundfunktionen: Oberfläche, **Suche über Titel, Inhalt und Schlagworte mit Trefferliste unter dem Feld**, Editor, Dunkelmodus |
| `t_link4.py` | Verlinken: Dialog, Seite anlegen, Rückverweise |
| `t_dup.py` | Kopieren einer Seite, unabhängige Verknüpfungen |
| `t_dupen.py` | dasselbe in englischer Oberfläche |
| `t_wikisyn.py` | `[[Seite]]` und `[[Text\|Seite]]`, Code bleibt Code |
| `t_refs.py` | Verweis-Panel, Zähler, gespeicherter Zustand, Gegenseitigkeit der Panels |
| `t_kopf.py` | Fluss-Knopf im Kopf: Umschalten, Reihenfolge der Knöpfe, **schmale Fenster** |
| `t_menue.py` | **Inhaltsverzeichnis links als Spalte: offen beim Öffnen, unter 640px zugeklappt, unter der Kopfzeile, drängt den Inhalt zur Seite, Fähnchen, kein Löschkreuz, Taste bleibt in ihrer Liste** |
| `t_panels.py` | **Panels rechts: geparkt genau auf der Fensterkante statt daneben** |
| `t_order.py` | Reihenfolge per Griff, Alt + Pfeil, Sperre bei der Suche, **Hinweis am Griff statt unter der Liste** |
| `t_file.py` | Wiki als Datei sichern und laden, fremde Datei |
| `t_mws.py` | Austausch mit MWS: JSON, Versionsprüfung, fremde Felder, doppelte Titel |
| `t_mwsmode.py` | **Betrieb auf einem MWS-Server** in zwölf Durchgängen: Marker, Speicher, Schreiben, 403, leere Wiki, Umbenennen, Serverausfall, das wegklickbare × am Serverhinweis |
| `t_anmeldung.py` | **Anmeldung und Schreibrechte: Statusabfrage, Name im Kopf, ausgeblendete Schreibknöpfe** |
| `t_login.py` | **Anmelden und abmelden: Link auf `/login?redirect=…`, Rückweg in diese Wiki, `POST /logout`, der Fall, dass es nicht klappt** |
| `t_speicher.py` | **eine Speicherabstraktion, zwei Ausprägungen: derselbe Vertrag in Browser und Server, und dass die laufende App ihn wirklich benutzt** |
| `t_mwsdatei.py` | **MWS-Modus an einer Datei: Auswahl am Marker, Verweise, Schreiben aus einer Datei und die sichtbare Fehlermeldung** |
| `t_abnahme.py` | **die fünf Abnahmepunkte: kein Nachladen, Doppelklick ohne Netz, Änderung bleibt, Store von außen** |
| `t_leerwiki.py` | leere Wiki-Datei, Vorlage füllen und öffnen, Angaben oben |
| `t_export.py` | **die gesicherte Datei wirklich auf die Platte schreiben und öffnen** |
| `t_fluss.py` | Fluss, Suche darin, Druckansicht als PDF |
| `t_scroll.py` | Scrollen im Fluss bei kurzem Fenster, Druck über mehrere Seiten |
| `t_werkzeug.py` | **die Werkzeugleiste unter dem Kopf**: Schalter, Wortzahl und Lesezeit, ablenkungsfreier Modus, Druck der offenen Seite, Austausch in `localStorage`, am Startseiten-Tiddler und im JSON |
| `t_markdown.py` | **Markdown hin und zurueck**: die offene Seite als `.md` sichern (Dateiname aus dem Titel), `.md`-Dateien als Seiten einlesen (Der Dateiname wird der Titel, Doppelte werden eindeutig, Verweise werden notiert, Anhaengen statt Ersetzen) |
| `t_kaestchen.py` | **Aufgabenlisten**: ein Kaestchen im Text anklicken aendert nur den Haken der Quellzeile und speichert die Seite, im Codeblock bleiben `[ ]` Text, ohne Schreibrecht bleibt das Kaestchen abgeschaltet |
| `t_seiteninhalt.py` | **Inhaltsverzeichnis der Seite**: Schalter in den Einstellungen, Liste der Ueberschriften aus der Vorschau (Ebenen, Codeblock aussen vor), Sprungziel vorhanden, Praeferenz im Browserspeicher und als Feld am Tiddler |
| `t_callout.py` | **Hinweiskaesten**: ein Zitat mit `[!NOTE]`/`[!HINWEIS]` und den uebrigen Marken wird ein farbiger Kasten mit Titelzeile, ein gewoehnliches Zitat bleibt Zitat, eine unbekannte Marke aendert nichts |
| `t_textur.py` | **die Textur kommt in beiden Modi an — und die CSS-Falle, die sie einmal verschluckt hat** |
| `t_abbrechen.py` | **Abbrechen bei einer frisch angelegten Seite**: die Hüllseiten leben auf Widerruf, Sichern macht sie dauerhaft |
| `t_klapp.py` | **Zuklappen im Verzeichnis**: der Zähler ist ein Anzeige-Ding dieser Ansicht, ab dem Neuladen wieder zugeklappt, nichts in `localStorage` |
| `t_hierarchie.py` | **das Feld `eltern`**: Tiefensuche-Reihenfolge, die Elternseite steht direkt vor ihrem Unterbaum, der wandert immer mit |
| `t_tags.py` | **Schlagworte stehen an der Seite, nicht im Text** — der Verweisgraph bleibt davon unberührt |
| `t_palette.py` | **die Farbwelten**: Auswahl im Einstellungen-Dialog, Hell und Dunkel darin, Austausch über `localStorage` bzw. Startseiten-Tiddler |
| `t_finger.py` | **der Fingerabdruck der Datei** entscheidet beim erneuten Öffnen, welche von zwei gestapelten Dateien gilt — ohne den Browserspeicher zu leeren |
| `t_buchhaltung.py` | **ohne Browser**: die Strukturtafel der README gegen `simplewiki.html`, die Fassung an allen drei `<meta>`-Stellen, die Zahl der Testdateien in README und AGENTS gegen `REIHENFOLGE` |

### Headless nimmt kein Fenster unter 500 Pixeln

Das ist keine Eigenheit dieses Projekts, das ist Chromium:

```
--window-size=320   ->  innerWidth=500
--window-size=380   ->  innerWidth=500
--window-size=412   ->  innerWidth=500
--window-size=600   ->  innerWidth=600
```

Zwei Tests wollten 380 Pixeln und haben **500** gemessen: `t_kopf.py` und
`t_menue.py`. Beide fragten `innerWidth <= 560`, und 500 erfüllt das — der
Test war grün und hatte trotzdem etwas anderes geprüft als behauptet.
Zwei Hebel wurden versucht und bringen nichts: `--force-device-scale-factor`
(ändert `innerWidth` nicht) und ein Rahmen um die Wiki (dessen Timer laufen
unter `--virtual-time-budget` nicht).

Wer es wirklich wissen will, muss es auf einem Bildschirm tun — im
Gerätemodus von Chrome oder auf einem Telefon. Bis dahin gilt: **ein Test,
der ein Fenster will, das es hier nicht gibt, sagt es im Bildschirm mit**,
statt eine Zahl zu behaupten. Beide tun das jetzt.

### Zwei Fallen, in die diese Suite schon getappt ist

**Ein Test, der nie läuft, ist grün.** `pruefe()` beendet das Skript — stand
ein Aufruf davon hinter einem `sys.exit`, lief er nie und niemand sah es, weil
das Skript danach ohnehin mit 0 endete. Zwei Dateien waren so gebaut
(`t_kopf.py`, `t_leerwiki.py`); beide melden ihre Prüfungen heute über
`pruefe()`, und ein absichtlich scheiternder Test wird rot.

**Eine Prüfung ohne Zahl ist eine Prüfung ohne Wirkung.** `alle.py` zählt nur,
was als `GESAMT: N bestanden, M fehlgeschlagen` dasteht. Ein Skript, das seine
Fehler zählt, aber seine bestandenen Prüfungen nicht meldet, trägt zur
Gesamtzahl **null** bei — die Prüfungen laufen, die Zahl lügt. Drei Dateien
waren so gebaut (`t_leerwiki.py`, `t_export.py`, `t_fluss.py`). Jedes Skript
meldet deshalb eine `GESAMT:`-Zeile, und `alle.py` liest keine andere.

**Auf *irgendeine* Änderung warten ist nicht warten.** `t_file.py` wartete
nach dem Einlesen auf irgendeinen Hinweis — und der erste kam vom Sichern zwei
Schritte vorher. Der Test las etwas, das er nie geprüft hatte, und meldete zu
Unrecht rot. Gewartet wird jetzt auf den Hinweis, den die Prüfung behauptet.

**Eine Position nach einer Animation ist dem Zufall überlassen.** Die
CSS-Transition fährt 300 ms, und unter Virtual Time läuft die Animationsuhr
nicht zuverlässig mit den Timern des Testskripts. `t_menue.py` misst
deshalb Positionen nur dort, wo noch nichts gefahren ist — beim ersten Bild —
und prüft die *Wirkung* des Zustands an der Klasse und an der CSS-Regel. Ein
Test, der an dieser Stelle „flackert", misst die Mitte der Fahrt.

### Eine Liste, ein Ort — und vorher zwei

Das Inhaltsverzeichnis stand eine Weile **zweimal** im Dokument: als Spalte
links und als Panel rechts, beide aus demselben Zustand. Wo ein Test
**zählte**, schrieb er deshalb `.toc-panel` davor — sonst wäre jede Seite
doppelt. Das Panel ist inzwischen weg, und mit ihm die Einschränkung.

Die Regel ist trotzdem nicht verschwunden, sie ist nur nicht mehr nötig:
**eine geordnete Rangfolge im Dokument ist keine Zugehörigkeit.**
`onZeileKeydown` nahm die Zeile für den Fokus aus dem ganzen Dokument
(`querySelectorAll('.toc-item')[ziel]`), und mit zwei Listen landete der
Fokus nach einem Alt+Pfeil in der anderen. Beim dritten Anlass — als es
wieder eine Auswahl gab, nämlich die Suche — heißt es wieder dasselbe: hol dir
deine Elemente aus deinem Bereich.

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
