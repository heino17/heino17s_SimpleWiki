# AGENTS.md

Was jemand wissen muss, der an diesem Wiki weiterarbeitet — und was ein
Werkzeug wissen muss, bevor es etwas anfasst.

Das meiste steht an der einen Stelle im Kopf von `simplewiki.html`: der
Austauschvertrag und der Betrieb mit dem MWS. **Lies die beiden Kommentare
oben im `<head>`, bevor du etwas änderst.** Dort steht, warum das Format so
aussieht und was der Server liefern muss.

---

## Was SimpleWiki ist

Eine HTML-Datei. `simplewiki.html` ist das ganze Programm: Oberfläche,
Editor, Markdown, Speicher und alle Bibliotheken (Vue, marked, TOAST UI inkl.
DOMPurify). Kein Server, kein Build, keine Installation.

## Wenn etwas mit dem MWS zu tun hat: vorher fragen

Die Wiki spricht mit dem MultiWikiServer über `/recipe/<name>/batch/…`.
**Bevor an dieser Schnittstelle, an den Feldern eines Tiddlers, an
`version`, am Marker oder am Austauschformat etwas geändert wird, muss
Rücksprache gehalten werden.** Das Wiki ist in eine andere Anwendung
eingebaut; eine Änderung, die hier nur „logisch" aussieht, kann dort etwas
kaputt machen, das man von hier aus nicht sieht.

Optische Änderungen — Farben, Abstände, Anordnung, Beschriftung — sind
freigegeben. Der Austausch mit dem Server ist es nicht.

## Provisionieren: nach jeder Änderung an `simplewiki.html`

```bash
cd <MWS-Quellbaum>
npm start provision-simplewiki <pfad>/simplewiki.html
```

Die Wiki liest ihre Schelle **aus dem Store, nicht aus dieser Datei**. Ohne
diesen Befehl ist alles genau wie vorher, auch nach einem Neustart des
Servers. Wer sich wundert, warum die eigene Änderung nicht ankommt, hat
fast immer diesen Schritt vergessen. Danach Strg+Umschalt+R.

Für `file://` gilt der Schritt nicht.

## Tests

```bash
python3 tests/alle.py            # alles, Endcode 0 = alles bestanden
python3 tests/alle.py fluss      # nur die Tests mit "fluss" im Namen
python3 tests/t_kopf.py          # einen einzelnen Test
```

Zwei Abhängigkeiten: **python3** und **chromium** im Pfad. Für die
Drucktests zusätzlich **`pdfinfo`** und **`pdftotext`**. Stand: 33
Testdateien, 1012 Prüfungen.

**Nach jeder Änderung an `simplewiki.html` die Suite laufen lassen.** Sie
prüft im echten Browser und hat schon Dinge gefunden, die kein Blick auf den
Bildschirm findet. Ein Test, der nicht läuft, ist schlimmer als keiner.

### Drei Fallen, die hier schon zugeschlagen sind

- **Headless nimmt kein Fenster unter 500 Pixeln.** `--window-size=380` ergibt
  `innerWidth=500`. Zwei Tests wollten 380 und haben 500 gemessen, ohne dass
  jemand es bemerkt hat. Ein Test, der ein Fenster will, das es hier nicht
  gibt, **sagt es im Bildschirm**, statt eine Zahl zu behaupten.
- **Eine Position nach einer CSS-Transition ist dem Zufall überlassen.**
  Unter `--virtual-time-budget` läuft die Animationsuhr nicht mit den Timern
  des Testskripts. Zustand und CSS-Regel prüfen, nicht die Mitte einer Fahrt.
- **Headless-Chromium ist ein Snap** und darf weder `/tmp` lesen noch dorthin
  schreiben. Testkopien gehören nach `tests/_kopien/`.

## Git

- **Nicht pushen.** Push bleibt eine ausdrueckliche Entscheidung.
- Committen ja, sobald ein Vorgang abgeschlossen ist — das ist eine
  ausdrückliche Erlaubnis.
- Nachrichten auf **ASCII** (ä → ae, ö → oe, ü → ue, ß → ss), wie es alle
  bisherigen Commit-Nachrichten tun.
- Der Betreff nennt die Änderung und, wenn es passt, die Prüfungszahl:
  `Neue Seite in den Kopf, links neben das Verzeichnis (700 Pruefungen)`.
- Der Rumpf sagt **warum**, nicht was. Das *was* steht im Diff.
- Eine Aussage im Betreff, die man nicht belegen kann, kommt nicht hinein.
  Eine Prüfungszahl wird erst genannt, wenn die Suite grün war.

## CHANGELOG

`CHANGELOG.md` wird nach Tag geführt, das Neueste zuerst, und jede
Überschrift nennt die Prüfungszahl des Stands danach. Nachgeschrieben wird
aus den Commit-Nachrichten, nicht erfunden. **Eine Prüfung ohne Zahl ist eine
Prüfung ohne Wirkung** — siehe `tests/README.md`.

## Was hier ausdrücklich nicht gemacht wird

- `tests/live_mws.py` wird **aus einem anderen Ordner** aufgerufen. Nicht
  einbauen, nicht „reparieren", nicht in die Suite hängen.
- Kein Abgleich mit anderen Ansichten (`/recipe/<name>/updates`): das
  Antwortformat ist nicht festgelegt.
- **Ein Element gehört zu seinem Bereich.** Nimm Zeilen, Knöpfe und Treffer aus
  dem Container, in dem sie stehen, nicht aus dem ganzen Dokument. Eine
  geordnete Rangfolge im Dokument ist keine Zugehörigkeit — es gab zwei
  Inhaltsverzeichnisse, und nach einem Alt+Pfeil sprang der Fokus in das
  andere. Das war zweimal teuer.
- Kein Login im Wiki: MWS prüft das Passwort mit OPAQUE, und die Bibliothek
  dafür lädt diese Wiki bewusst nicht.
- Keine Bilder in Wiki-Dateien. Wer Inhalte mit Bildern übergibt, verliert
  sie, und sollte das vorher sagen.
