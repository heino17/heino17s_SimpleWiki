# 🇺🇸 SimpleWiki

[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](LICENSE)

---

A wiki that is **a single file**.

`simplewiki.html` is the whole program: interface, editor, Markdown, storage
and every library live inside it. No server, no build, no installation.
Whoever double-clicks the file has a wiki; whoever passes it on hands over a
wiki — with the content its author put in.

That is the whole idea. Everything else is shape given to it.

**SimpleWiki is developed first of all for use in MWS-wikiwise
(MultiWikiServer-wikiwise), not as a standalone, independent file.** It can be
used on its own — but then every change has to be written back into the file by
hand. In MWS-wikiwise all of that runs automatically. The file in this
repository is the empty template; an MWS wiki starts empty, too.

## 🚀 Getting started

```bash
xdg-open simplewiki.html          # or double-click it in your file manager
```

A fresh wiki starts empty: the start screen names the first step and, for
whoever may write, offers a button for the first page. From there: ☰ opens the
table of contents, "+ New page" creates one, the button at the bottom right
switches the editor on.

For the tests:

```bash
python3 tests/alle.py             # everything
python3 tests/alle.py fluss       # only the tests with "fluss" in the name
python3 tests/t_order.py          # a single test
```

## ✨ What's inside

| | |
|---|---|
| **Writing** | Markdown, in the WYSIWYG editor (TOAST UI) or in the plain text field; a page just created disappears again if you then click "Cancel" |
| **Indent** | the two buttons in the toolbar move text a level in or back out: a list item nests or flattens, every other paragraph becomes a quote (`> `) and back |
| **New page** | a button in the header, left of the contents — gone for anyone who may not write; the new page is appended to the contents |
| **Contents** | as a left column, pushes the content aside and keeps the header clear; foldable at the little flag, starts folded below a 640px window width |
| **Linking** | `[[Page]]` and `[[Label\|Page]]` in the text, plus a dialog while editing |
| **Backlinks** | incoming and outgoing links in their own panel, with a counter in the header |
| **Outline** | sub-pages under a parent page, arbitrarily deep; built by dragging (three zones per row: before, as a child, after) or with Alt + arrow: ↑/↓ on the same level, → indent, ← outdent |
| **Folding** | after a reload only the top level shows: parent pages with sub-pages carry a ▼ counter and come folded (the arrow on the left does the same); unfold at the counter, with the right arrow or by clicking — none of it lands in the file |
| **Duplicate** | creates a copy with its own name, with no link to the original |
| **Search** | in the header; it searches title, content **and tags**, with the hits right below — and it is the only way to find something while the contents are folded |
| **Flow** | read all pages one after another and print them as a PDF |
| **Toolbar** | a row below the header, off by default and switched on in the settings dialog: word count and reading time of the open page, distraction-free reading (⛶, leaves with Escape), and the print of **just this page** |
| **Markdown** | save the open page as a `.md` file (the file name carries the title); load one or more `.md` files as new pages (the file name without its extension becomes the title, the pages are added, not replaced) |
| **Task lists** | a `- [ ]` in the text becomes a checkbox you can click while reading; the click changes only the tick in the line and saves the page. Where you may not write, the boxes stay switched off |
| **Page contents** | a switch in the settings dialog shows a list of the open page's headings above the text; a click jumps to the heading. The list is read from the finished view, so code blocks stay out of it |
| **Callouts** | a quote that begins with `> [!NOTE]` (also `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]` and the German tags `[!HINWEIS]`, `[!TIPP]`, `[!WICHTIG]`, `[!WARNUNG]`, `[!ACHTUNG]`) becomes a coloured box with a title. Every other quote stays a quote |
| **Undo** | the ↶ button in the toolbar takes back the last change to the content — a deleted page, an edited text, a freshly created page. One step, not a history |
| **Light / dark** | also in the editor; the 🌙/☀️ switch stays in every colour world |
| **Colour worlds** | nine moods — Pergament, Nord, Wacholder, Sol, Flexoki, Vanille, Wüste, Dämmerung and the **Own** one; each with a light and a dark branch, selectable in the settings dialog. The Own one grows from a cloned world and can be set colour by colour |
| **Language** | eight languages (German, English, Russian, Spanish, French, Japanese, Korean, Chinese), built in |
| **Exchange** | save and load the wiki as a file, export JSON, export an empty template |

A wiki consists of **text pages**. There are no images: whoever hands over
content with images loses them, and should say so beforehand.

## 🗂️ How the file is built

`simplewiki.html` is 8675 lines long and has these parts, always in the same
order:

```
       1–221  two comments in the <head>: the exchange contract and the
              MWS operation. They are the real documentation — this is
              where it says why the format looks as it does and what the
              server must deliver.
         222  <script id="simplewiki-daten">  the data island
     226–360  the embedded libraries (marked, Vue, TOAST UI incl.
              DOMPurify)
    361–2920  the stylesheet
        2930  the store point behind which the server inserts its tiddlers
    2933–3498  the interface (Vue template)
    3500–8675  the program
```

The two comments in the header are **ordinary HTML and no ballast**: whoever
reads the file reads the contract there first. Two things there need special
care when changing:

- The exchange contract describes the structure of the data island and what
  happens on reading (unknown fields stay, files that are too new are
  rejected outright, a file without pages is not taken over).
- The MWS section names the point in the document behind which the server
  inserts its tiddlers — **without quoting the point as a string**. MWS
  searches for it literally and takes the first hit in the document, even one
  inside a comment. A comment quoting it would swallow the tiddlers into
  itself: the wiki would stand there beautifully empty. The rule holds
  without exception — the text appears exactly once in the raw file.

## 🔀 The two modes

At **exactly one** place in the program it says where the pages come from
(`simplewiki.html:3391`, "Where the pages live: browser or MWS"):

- **Browser** — the normal case. Pages live in `localStorage`. A file opened
  by double-click remembers in exactly the same way.
- **MWS-wikiwise** (MultiWikiServer-wikiwise) — a server that serves SimpleWiki
  writes calls to `$tw.preloadTiddler` behind the point in the header, one per
  tiddler. When
  tiddlers arrive, they are read from there and written back there. One line
  above the content says where the pages come from; the **×** at its edge
  hides it for the rest of the session (its state survives a reload, not
  closing the wiki).

Both stores speak the same methods (`laden`, `uebernehmen`, `seiteSichern`,
`seiteLoeschen`, `startseiteSetzen`, `themaSetzen`, `spracheSetzen`,
`toolbarSetzen`, `status`,
`abmelden`). The rest of the program does not know the difference. If the
point is not there or no tiddlers arrive, everything stays in the browser.

## 🔌 What SimpleWiki says to the server

| Call | What for |
|---|---|
| `GET /recipe/<name>/status` | who is logged in and whether this tab may write |
| `PUT /recipe/<name>/batch/list` | fetch all tiddlers |
| `PUT /recipe/<name>/batch/read` | fetch specific tiddlers |
| `PUT /recipe/<name>/batch/save` | write |
| `PUT /recipe/<name>/batch/delete` | delete |
| `PUT /recipe/<name>/shell/update` | adopt the interface to the newest template version (only the owner and administrators) |
| `POST /logout` | delete the session (response 204) |
| `/login?redirect=/wiki/<name>` | login — a link, because it is the server's business |

All calls carry the header `X-Requested-With: fetch`. Batch calls are
**PUT, not POST**; that is fixed in `RecipeRoutes.ts` of MWS-wikiwise.

For the interface, the server says which template version this wiki is on
(the response of `/status` carries it under `shell`). The interface names its
own version via `<meta name="mws-shell-version" content="v0.1.41">` in the
head of `simplewiki.html` — this name appears in the admin app and in the
update hint instead of the counting release number and is raised with every
interface change. A wiki with the policy **notify** for which a newer version
is ready shows a sign only to the **owner** and the **administrators**: a dot
on the gear (⚙️) and, in the **Settings** dialog, a hint with a button
"Adopt" — which calls `PUT /recipe/<name>/shell/update`, the server moves the
pin to the newest version, and the wiki reloads. The button carries a tip:
**The contents of your wiki are not changed by this update!** The hint is
dismissed per offered version — either until a new offer or for a month.
Whoever may only write does not see the hint: adopting an interface is an
ownership decision.

Four operating states, all recognized at the server and not guessed:

- **nobody logged in** → "Not logged in" as a **link** to `/login` (with the
  way one came from — whoever clicks "Log in" in a wiki wants to be back in
  that wiki afterwards)
- **logged in, but no write permission** → a read-only hint, and the write
  buttons are **gone**, not just grey
- **session expires mid-way** → the app notices it on the next write attempt
  and switches without a reload
- **the server does not answer at all** → nothing is invented: no read-only
  state, no lost write buttons. An outage is not a permission problem.

## 🔄 The exchange format

Lives in the data island and can be written and read as its own `.json` file:

```json
{
  "version": 1,
  "seiten": [
    {"id": "…", "title": "…", "content": "Markdown with [[links]]",
     "links": ["page name"], "tags": [], "created": "ISO-8601 with Z",
     "updated": "ISO-8601 with Z",
     "eltern": "title of the parent page (only for sub-pages)"}
  ],
  "startseite": "id of the start page",
  "sprache": "de",
  "thema": "light",
  "toolbar": true
}
```

Three promises:

1. **JSON and HTML are equivalent.** On reading, JSON is tried and only
   accepted if it contains a `seiten` array; otherwise the data block of the
   HTML file applies.
2. **Foreign fields stay.** `normiereSeiten` normalizes the known fields and
   carries everything else along unchanged — a round trip through a tool
   loses nothing. This holds on the page level as on the top level (`autor`,
   `herkunft`, `exportdatum` …).
3. **Files that are too new are rejected outright.** If `version` is missing
   or larger than one's own, nothing is taken over and the reason is named.

Linking is done via `title`, not via `id` — that is why no two pages may have
the same name. When creating, a name already taken is quietly made unique
("New page 2"); when renaming, it is rejected and the name is named: silent
renaming on save would be surprising.

## 🛠️ Provision after every change

**The wiki reads its shell from the store, not from this file.** So after a
change to `simplewiki.html`, without this command everything is exactly as
before — even after a restart of the server:

```bash
cd <MWS-wikiwise source tree>
npm start provision-simplewiki <path>/simplewiki.html
```

The command reports `Template "SimpleWiki" updated`; after that the browser
only needs a hard reload (Ctrl+Shift+R). Whoever wonders why their own change
does not arrive has almost always forgotten this step.

## ✅ Tests

The tests check `simplewiki.html` in a **real browser**: each test builds an
instrumented copy of the wiki, opens it in Chromium and then reads the report
that the test script deposited in the page itself.

```bash
python3 tests/alle.py            # everything, exit code 0 = all passed
python3 tests/alle.py mws        # only the tests with "mws" in the name
python3 tests/t_fluss.py         # a single test
```

- **35 test files**, 1040 checks per suite run; the two print tests start
  Chromium a second time for the PDF.
- One test is **not** in `alle.py`, because it starts a real server:
  `tests/live_mws.py` checks the wiki against a **real** MWS-wikiwise
  instead of the test fixture from `mwsserver.py`. See `tests/README.md`.

Dependencies: **python3**, **chromium** on the path, and for the two print
tests additionally **`pdfinfo`** and **`pdftotext`** (poppler-utils).

It is worth reading `tests/README.md` — it lists the test files, what the
test mechanism does exactly, and two lessons from the tests that shaped the
program:

> **Test the task, not the implementation.** When saving, a test once said
> "interface empty in the result" — which checked that the file is broken.
> The test was green and the function broken.
>
> **Test with the window it is used in.** The flow could not be scrolled and
> printing lost everything after screen height. Both only surfaced because
> the test checks with a window of 900×420 pixels.

## 📦 Bundled libraries

All embedded rather than loaded from a CDN — a strict Content-Security-Policy
allows only `self`, and a wiki should run without a network, too.

| Library | Version | License |
|---|---|---|
| Vue 3 | 3.5.43 | MIT |
| marked | 15.0.12 | MIT |
| TOAST UI Editor | 3.2.2 | MIT |
| DOMPurify (bundled in TOAST UI Editor) | 2.3.3 | Apache-2.0 or MPL-2.0 |
| tslib (bundled in TOAST UI Editor) | – | 0BSD |

The full license texts and copyright notices are in
[THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md).

## 🚧 Limits that are on purpose

- **One file, one user.** There is no server administration, no simultaneous
  editors, no rights management in the wiki itself — that comes from
  MWS-wikiwise when it is there.
- **No images.** See above.
- **No syncing with other views.** The endpoint
  `/recipe/<name>/updates?since=<seq>` is not called, because its response
  format is not fixed. Every change goes out immediately, a reload shows the
  server's state.
- **No login in the wiki.** MWS-wikiwise checks the password with OPAQUE, and
  for that this wiki deliberately loads no plugins: it fetches its pages via
  `/recipe`. Rebuilding it would mean putting a second megabyte of WebAssembly
  into every wiki page. Logging out works from here, because there is nothing
  to prove.

## 📁 Folder

```
simplewiki.html      the whole wiki
tests/               tests, test helpers, test fixtures (see tests/README.md)
tests/_kopien/       copies, PDFs and images of the test runs – not committed
.gitignore
```

## 📄 License

This project is licensed under the [BSD 3-Clause License](LICENSE) – free to
use, modify and redistribute, including commercially. Copyright (c) 2026,
heino17. The licenses of the bundled third-party libraries are listed in
[THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md).

---

# 🇩🇪 SimpleWiki

[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](LICENSE)

---

Ein Wiki, das **eine einzige Datei** ist.

`simplewiki.html` ist das ganze Programm: Oberfläche, Editor, Markdown,
Speicher und alle Bibliotheken stecken darin. Kein Server, kein Build, keine
Installation. Wer die Datei doppelklickt, hat ein Wiki; wer sie weiterreicht,
gibt ein Wiki weiter — mit dem Inhalt, den sein Ersteller darin abgelegt hat.

Das ist der ganze Gedanke. Alles Weitere ist Ausgestaltung davon.

**SimpleWiki wird zuerst für den Einsatz in MWS-wikiwise
(MultiWikiServer-wikiwise) entwickelt, nicht als eigenständige, unabhängige
Datei.** Einzeln lässt sie sich verwenden — dann muss jede Änderung von Hand
zurück in die Datei geschrieben werden. In MWS-wikiwise läuft das alles
automatisch. Die Datei in diesem Repository ist die leere Vorlage; eine
MWS-Wiki startet ebenfalls leer.

## 🚀 Loslegen

```bash
xdg-open simplewiki.html          # oder: im Dateimanager doppelklicken
```

Eine frische Wiki startet leer: die Startfläche nennt den ersten Schritt und
bietet, wer schreiben darf, einen Knopf für die erste Seite. Von dort aus: ☰
öffnet das Inhaltsverzeichnis, „+ Neue Seite“ legt eine an, der Knopf unten
rechts schaltet den Editor ein.

Für die Tests:

```bash
python3 tests/alle.py             # alles
python3 tests/alle.py fluss       # nur die Tests mit "fluss" im Namen
python3 tests/t_order.py          # einen einzelnen Test
```

## ✨ Was drin ist

| | |
|---|---|
| **Schreiben** | Markdown, im WYSIWYG-Editor (TOAST UI) oder im reinen Textfeld; eine eben angelegte Seite verschwindet wieder, wer danach «Abbrechen» klickt |
| **Einrücken** | die zwei Knöpfe in der Werkzeugleiste schieben Text eine Ebene ein oder wieder heraus: ein Listenpunkt verschachtelt oder flacht ab, jeder andere Absatz wird zu einem Zitat (`> `) und wieder zurück |
| **Neue Seite** | ein Knopf im Kopf, links vom Verzeichnis — weg, wer nicht schreiben darf; die neue Seite kommt unten ins Verzeichnis |
| **Inhaltsverzeichnis** | als Spalte links, drängt den Inhalt zur Seite und lässt die Kopfzeile frei; am Fähnchen zu- und aufklappbar, unter 640px Fensterbreite fängt es zugeklappt an |
| **Verlinken** | `[[Seite]]` und `[[Beschriftung\|Seite]]` im Text, dazu ein Dialog beim Bearbeiten |
| **Verweise** | Rück- und Ausgehende in einem eigenen Panel, mit Zähler im Kopf |
| **Gliederung** | Unter-Seiten unter einer Elternseite, beliebig tief; gebaut per Ziehen (drei Zonen je Zeile: davor, als Kind, dahinter) oder mit Alt + Pfeil: ↑/↓ auf gleicher Ebene, → einrücken, ← ausrücken |
| **Zuklappen** | Beim Neuladen steht nur die oberste Ebene: Elternseiten mit Unter-Seiten tragen einen Zähler ▼ und kommen zugeklappt (Pfeil links tut dasselbe); aufklappen am Zähler, mit Pfeil rechts oder durch Anklicken — nichts davon landet in der Datei |
| **Duplizieren** | legt eine Kopie mit eigenem Namen an, ohne Verknüpfung zur Vorlage |
| **Suche** | im Kopf; sie sucht Titel, Inhalt **und Schlagworte**, die Treffer stehen direkt darunter — und sie sind der einzige Weg, etwas zu finden, wenn das Verzeichnis zugeklappt ist |
| **Fluss** | alle Seiten hintereinander lesen und als PDF drucken |
| **Werkzeugleiste** | eine Zeile unter dem Kopf, standardmäßig aus und im Einstellungen-Dialog einschaltbar: Wortzahl und Lesezeit der offenen Seite, ablenkungsfreies Lesen (⛶, verlässt sich mit Escape) und der Druck **genau dieser Seite** |
| **Markdown** | die offene Seite als `.md`-Datei sichern (der Dateiname trägt den Titel); eine oder mehrere `.md`-Dateien als neue Seiten laden (der Dateiname ohne Endung wird der Titel, die Seiten kommen dazu statt zu ersetzen) |
| **Aufgabenlisten** | aus einem `- [ ]` im Text wird ein Kästchen, das beim Lesen angeklickt werden kann; der Klick ändert nur den Haken in der Zeile und speichert die Seite. Wo nicht geschrieben werden darf, bleiben die Kästchen abgeschaltet |
| **Inhaltsverzeichnis der Seite** | ein Schalter in den Einstellungen legt über den Text ein Verzeichnis seiner Überschriften; ein Klick springt zur Überschrift. Die Liste kommt aus der fertigen Vorschau, ein Codeblock bleibt damit außen vor |
| **Hinweiskästen** | ein Zitat, das mit `> [!NOTE]` beginnt (`[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]` sowie deutsch `[!HINWEIS]`, `[!TIPP]`, `[!WICHTIG]`, `[!WARNUNG]`, `[!ACHTUNG]`), wird ein farbiger Kasten mit Titelzeile; jedes andere Zitat bleibt ein Zitat |
| **Rückgängig** | der ↶-Knopf in der Werkzeugleiste nimmt die letzte Änderung am Inhalt zurück — eine gelöschte Seite, ein geänderter Text, eine frisch angelegte Seite. Ein Schritt, keine Chronik |
| **Hell / Dunkel** | auch im Editor; die 🌙/☀️-Achse bleibt in jeder Farbwelt |
| **Farbwelten** | neun Stimmungen — Pergament, Nord, Wacholder, Sol, Flexoki, Vanille, Wüste, Dämmerung und die **Eigene**; jede mit hellem und dunklem Zweig, im Einstellungen-Dialog wählbar. Die Eigene entsteht aus einer geklonten Welt und lässt sich Farbe für Farbe einstellen |
| **Sprache** | acht Sprachen (Deutsch, Englisch, Russisch, Spanisch, Französisch, Japanisch, Koreanisch, Chinesisch), fest eingebaut |
| **Austausch** | Wiki als Datei sichern und laden, JSON exportieren, leere Vorlage exportieren |

Eine Wiki besteht aus **Textseiten**. Es gibt keine Bilder: wer Inhalte mit
Bildern übergibt, verliert sie, und sollte das vorher sagen.

## 🗂️ Wie die Datei aufgebaut ist

`simplewiki.html` ist 9837 Zeilen lang und hat diese Teile, immer in derselben
Reihenfolge:

```
       1–228  zwei Kommentare im <head>: der Austauschvertrag und der
              MWS-Betrieb. Sie sind die eigentliche Dokumentation — hier
              steht, warum das Format so aussieht und was der Server
              liefern muss.
         229  <script id="simplewiki-daten">  die Dateninsel
     233–367  die eingebetteten Bibliotheken (marked, Vue, TOAST UI inkl.
              DOMPurify)
    368–3159  das Stylesheet
        3169  der Store-Punkt, hinter dem der Server seine Tiddler einsetzt
    3172–3805  die Oberfläche (Vue-Template)
    3807–9837  das Programm
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

## 🔀 Die zwei Betriebsarten

An **genau einer** Stelle im Programm steht, woher die Seiten kommen
(`simplewiki.html:3391`, „Wo die Seiten liegen: Browser oder MWS“):

- **Browser** — der Normalfall. Seiten liegen in `localStorage`. Eine per
  Doppelklick geöffnete Datei merkt sich genau so.
- **MWS-wikiwise** (MultiWikiServer-wikiwise) — ein Server, der SimpleWiki
  ausliefert, schreibt hinter den Punkt im Kopf Aufrufe von
  `$tw.preloadTiddler`, eines je Tiddler.
  Kommen Tiddler an, wird von dort gelesen und dorthin geschrieben. Eine Zeile
  über dem Inhalt sagt, woher die Seiten kommen; das **×** an ihrem Rand
  blendet sie für den Rest der Session aus (ihr Zustand überlebt das
  Neuladen, nicht das Schließen der Wiki).

Beide Speicher sprechen dieselben Methoden an (`laden`, `uebernehmen`,
`seiteSichern`, `seiteLoeschen`, `startseiteSetzen`, `themaSetzen`,
`spracheSetzen`, `toolbarSetzen`, `status`, `abmelden`). Der Rest des Programms
kennt den Unterschied nicht. Steht der Punkt nicht da oder kommen keine Tiddler an,
bleibt alles im Browser.

## 🔌 Was SimpleWiki mit dem Server spricht

| Aufruf | Wofür |
|---|---|
| `GET /recipe/<name>/status` | wer angemeldet ist und ob dieser Tab schreiben darf |
| `PUT /recipe/<name>/batch/list` | alle Tiddler holen |
| `PUT /recipe/<name>/batch/read` | bestimmte Tiddler holen |
| `PUT /recipe/<name>/batch/save` | schreiben |
| `PUT /recipe/<name>/batch/delete` | löschen |
| `PUT /recipe/<name>/shell/update` | Oberfläche auf die neueste Template-Version übernehmen (nur Besitzerin und Administratoren) |
| `POST /logout` | Sitzung löschen (Antwort 204) |
| `/login?redirect=/wiki/<name>` | Anmeldung — ein Link, weil sie Sache des Servers ist |

Alle Aufrufe mit dem Kopf `X-Requested-With: fetch`. Stapelaufrufe sind
**PUT, nicht POST**; so ist es in `RecipeRoutes.ts` von MWS-wikiwise
festgeschrieben.

Der Server sagt für die Oberfläche auf, auf welcher Template-Version diese
Wiki steht (die Antwort von `/status` trägt das unter `shell`). Die
Oberfläche nennt ihre Version selbst über
`<meta name="mws-shell-version" content="v0.1.31">` im Kopf von
`simplewiki.html` — dieser Name erscheint in der Verwaltung und im
Update-Hinweis statt der zählenden Release-Nummer und wird bei jeder
Oberflächenänderung erhöht. Ein Wiki mit
der Politik **notify**, für das eine neuere Version bereitliegt, zeigt nur
der **Besitzerin** und den **Administratoren** ein Zeichen: ein Punkt am
Zahnrad (⚙️) und im **Einstellungen**-Dialog ein Hinweis mit einem Knopf
„Übernehmen“ — der ruft `PUT /recipe/<name>/shell/update` auf, der Server
verschiebt den Pin auf die neueste Version, und die Wiki lädt neu. Der
Knopf trägt einen Tipp: **Die Inhalte Deines Wikis werden bei diesem
Update nicht verändert!** Weggedrückt wird der Hinweis je angebotener
Version — entweder bis zu einem neuen Angebot oder für einen Monat. Wer
nur schreiben darf, sieht den Hinweis nicht: eine Oberfläche übernehmen
ist eine Eigentumsentscheidung.

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

## 🔄 Das Austauschformat

Steckt in der Dateninsel und lässt sich als eigene `.json`-Datei schreiben und
lesen:

```json
{
  "version": 1,
  "seiten": [
    {"id": "…", "title": "…", "content": "Markdown mit [[Verweisen]]",
     "links": ["Seitenname"], "tags": [], "created": "ISO-8601 mit Z",
     "updated": "ISO-8601 mit Z",
     "eltern": "Titel der Elternseite (nur bei Unter-Seiten)"}
  ],
  "startseite": "id der Startseite",
  "sprache": "de",
  "thema": "light",
  "toolbar": true
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

## 🛠️ Nach jeder Änderung provisionieren

**Die Wiki liest ihre Schale aus dem Store, nicht aus dieser Datei.** Nach
einer Änderung an `simplewiki.html` ist deshalb ohne diesen Befehl alles
genau wie vorher — auch nach einem Neustart des Servers:

```bash
cd <MWS-wikiwise-Quellbaum>
npm start provision-simplewiki <pfad>/simplewiki.html
```

Der Befehl meldet `Template "SimpleWiki" updated`; danach muss der Browser
nur noch hart neu laden (Strg+Umschalt+R). Wer sich wundert, warum die eigene
Änderung nicht ankommt, hat fast immer diesen Schritt vergessen.

## ✅ Tests

Die Tests prüfen `simplewiki.html` im **echten Browser**: Jeder Test baut eine
instrumentierte Kopie der Wiki, öffnet sie in Chromium und liest danach den
Bericht aus, den das Testskript in der Seite selbst ablegt.

```bash
python3 tests/alle.py            # alles, Endecode 0 = alles bestanden
python3 tests/alle.py mws        # nur die Tests mit "mws" im Namen
python3 tests/t_fluss.py         # einen einzelnen Test
```

- **42 Testdateien**, 1180 Prüfungen pro Suite-Lauf; die beiden Drucktests
  starten Chromium ein zweites Mal für das PDF.
- Ein Test steht **nicht** in `alle.py`, weil er einen echten Server startet:
  `tests/live_mws.py` prüft die Wiki gegen ein **echtes** MWS-wikiwise statt
  gegen die Testfigur aus `mwsserver.py`. Siehe `tests/README.md`.

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

## 📦 Mitgebrachte Bibliotheken

Alle fest eingebettet statt vom CDN geladen — eine strikte
Content-Security-Policy erlaubt nur `self`, und eine Wiki soll auch ohne Netz
laufen.

| Bibliothek | Version | Lizenz |
|---|---|---|
| Vue 3 | 3.5.43 | MIT |
| marked | 15.0.12 | MIT |
| TOAST UI Editor | 3.2.2 | MIT |
| DOMPurify (in TOAST UI Editor enthalten) | 2.3.3 | Apache-2.0 oder MPL-2.0 |
| tslib (in TOAST UI Editor enthalten) | – | 0BSD |

Die vollständigen Lizenztexte und Copyright-Hinweise stehen in
[THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md).

## 🚧 Grenzen, die Absicht sind

- **Eine Datei, ein Nutzer.** Es gibt keine Serververwaltung, keine
  gleichzeitigen Bearbeiter, keine Rechteverwaltung im Wiki selbst — das
  kommt vom MWS-wikiwise, wenn es da ist.
- **Keine Bilder.** Siehe oben.
- **Kein Abgleich mit anderen Ansichten.** Der Endpunkt
  `/recipe/<name>/updates?since=<seq>` wird nicht aufgerufen, weil sein
  Antwortformat nicht festgelegt ist. Jede Änderung geht sofort raus, ein
  Neuladen zeigt den Stand des Servers.
- **Kein Login im Wiki.** MWS-wikiwise prüft das Passwort mit OPAQUE, und
  dafür lädt diese Wiki bewusst keine Plugins: sie holt ihre Seiten über
  `/recipe`. Es
  nachzubauen hieße, ein zweites Megabyte WebAssembly in jede Wiki-Seite zu
  legen. Abmelden geht von hier aus, weil es nichts zu beweisen gibt.

## 📁 Ordner

```
simplewiki.html      das ganze Wiki
tests/               Tests, Testhilfen, Testfiguren (siehe tests/README.md)
tests/_kopien/       Kopien, PDFs und Bilder der Testläufe – nicht committet
.gitignore
```

## 📄 Lizenz

Dieses Projekt steht unter der [BSD-3-Clause-Lizenz](LICENSE) – frei
nutzbar, veränderbar und weitergebbar, auch kommerziell. Copyright (c) 2026,
heino17. Die Lizenzen der mitgelieferten Fremdbibliotheken stehen in
[THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md).
