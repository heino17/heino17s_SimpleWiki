# Änderungen

Nach Tag, das Neueste zuerst. Wo eine Überschrift eine Prüfungszahl nennt, ist
das der Stand der Suite nach diesem Schritt (`python3 tests/alle.py`).

Es gibt noch keine Versionsnummer. Eine zu erfinden, die niemand erhöht, wäre
schlechter als ein Datum — deshalb wird nach Tag datiert.

---

## 2026-10-05

### Tiefe: Schatten unter dem Kopf, Schraffur im Kopf und Punktraster im Text — 708 Prüfungen

Drei Dinge, die die Oberfläche von „flach" zu „mit Tiefe" holen. Alle drei
sind eine einzige Sache: Licht von oben.

- **Der Kopf bekommt einen Schatten** (`0 3px 10px`). Er liegt über dem Text
  und soll sich auch so fühlen, statt eine Linie über einer Fläche zu sein.
  Der Schatten hängt am Kopf, nicht am Inhalt — er wandert mit.
- **Der Kopf bekommt eine Schraffur**: feine Linien im 45-Grad-Winkel, alle
  7 Pixel.
- **Der Textbereich und das Verzeichnis bekommen dasselbe Punktraster**, alle
  14 Pixel.

Warum ausgerechnet Punkte hinter dem Text und keine Linien: schräge Linien
hinter laufendem Text flimmern, Punkte nicht. Der Kopf hat keine langen
Zeilen und darf darum schraffiert sein.

**Das Punktraster stand zuerst bei 0.028 und war zu schwach** — der Nutzer hat
es „fast nicht gesehen" und auf **0.05** gesetzt, also so stark wie die
Schraffur. Das war nicht gerechnet, sondern angesehen; die Zahl im Kommentar
sagte vorher „noch feiner" und war damit ebenfalls falsch.

Das Muster selbst steht jetzt an **einer** Stelle (`--textur-bild`) und wird von
beiden Benutzern geholt. Sonst läuft hier eine Zahl und dort eine andere, und
wer die eine ändert, merkt von der anderen nichts.

**Was nicht stimmt, ist hier benannt:** die Punktreihen treffen sich über die
Kante zwischen Verzeichnis und Text, die Spalten nicht — der Text beginnt um
die Breite des Verzeichnisses seitlich, und die ist kein Vielfaches der
Rasterweite. Bei dieser Stärke sieht man es nicht.

Im Dunklen wird dasselbe Muster mit **Licht** gezeichnet statt mit Tinte: ein
heller Strich auf hellem Grund wäre im Hellen ein dunkler.

Und auf Papier kommt nichts davon: `t_fluss.py` prüft jetzt, dass die Druckregel
Textur und Schatten abschaltet. Aus einem Punktraster werden im Druck vier
Graustufen, und den Schmutzfleck hat niemand bestellt.

**Und dabei ist ein Test zweimal rotgelaufen, der nichts mit der Textur zu
tun hatte.** `t_file.py` wartete nach dem Einlesen auf *irgendeinen* Hinweis —
und der erste kam vom Sichern zwei Schritte vorher und nennt keine
Seitenzahl. Der Test las einen Hinweis, den er nie geprüft hatte, und meldete
zu Unrecht rot. Er wartet jetzt auf **den** Hinweis, den er behauptet: auf
*irgendeine* Änderung zu warten ist nicht dasselbe wie auf das Gesuchte.

**705 → 708 Prüfungen**, 23 Testdateien.

### Der Fuß des Verzeichnisses ist weg — 705 Prüfungen

Der Hinweis auf die Reihenfolge stand als Zeile unter der Liste, mit einer
Trennlinie darüber. Er steht jetzt **am Griff**, wo er hingehört: `⠿ tragen,
Alt + ↑/↓, oder mit einem Klick ansehen` — man braucht ihn nur, wenn man
anfasst, und dann ist er genau dort. Bei einer laufenden Suche nennt der
Tooltip den anderen Weg.

Damit ist `.toc-footer` ganz weg, mit ihm seine CSS-Regeln und sein Eintrag
in der Druckliste. `.toc-hint` ebenfalls — es gab nichts mehr, wofür es
galt.

**Und ein Fehler von mir, den der Nutzer im Bildschirm gefunden hat.** Beim
Einfügen der Suchfeld-Liste hatte ich **zwei Kommentar-Anfänge und ein
Ende** geschrieben. Der mittlere Absatz stand als **Text in der Kopfzeile** —
zwischen Titel und Suchfeld, in jedem Fenster. Kein Test hat es gesehen: die
Knöpfe waren alle da, die Reihenfolge stimmte, nur der Raum dazwischen war
voller Text.

Deshalb prüft `t_kopf.py` jetzt den **ganzen Text** des Kopfs gegen das, was
auf seinen Knöpfen steht. Ein Kommentar, der zu früh oder zu spät
geschlossen wird, fällt damit auf — und nicht erst beim Ansehen. Am
kaputten Stand nachgewiesen: die Prüfung meldet genau das, was der Nutzer
gesehen hat.

**704 → 705 Prüfungen**, 23 Testdateien.

### Das rechte Verzeichnis ist weg, die Suche steht unter dem Feld — 703 Prüfungen

Das Panel rechts und der Knopf ☰ im Kopf sind entfernt. Was bleibt, ist
**ein** Inhaltsverzeichnis: die Spalte links.

Das war nur möglich, weil vorher zwei Orte dasselbe zeigten — und weil die
Suche in dem einen stand, den man erst aufmachen musste. Jetzt steht sie da,
wo man ohnehin hinsieht.

**Die Treffer kommen direkt unter das Suchfeld.** Sie hängen an einem Rahmen,
der das Feld und den Knopf zum Leeren umfasst, und sind so breit wie dieser
Rahmen. Sie erscheinen nur, wenn wirklich etwas gesucht wird — ein Feld, das
beim Lesen im Weg hängt, ist ein Fehler.

- **Die Auswahl räumt die Suche weg.** Hielt man sie fest, bliebe das
  Verzeichnis auf die Treffer gefiltert und man sähe die übrigen Seiten
  nicht mehr — obwohl man gerade in einer davon liest.
- **Escape nimmt sie zuerst**, denn sie liegt über allem, und die Panels sind
  danach ohnehin zu. Suche geht vor Panels.
- Die Liste steht **nicht** im Druck, wie alles Bedienende dort.
- Das Verzeichnis links filtert **weiterhin** mit — das war schon so und
  wird von mehreren Tests geprüft. Die Liste unter dem Feld ist der
  zusätzliche Weg, und der einzige, der noch da ist, wenn das Verzeichnis
  zugeklappt ist: auf einem schmalen Fenster ist es das immer.

Der **Hinweis auf die Reihenfolge** ist aus dem Fuß des rechten Panels in
den Fuß des Menüs gewandert — er gehört zu den Zeilen mit den Griffen, und
die stehen links.

Mitgegangen: `showToc`, `openToc`, `onSearchInput`, die CSS für `.menu-toggle`
und für das zweite Suchfeld im Panel, und der Knopf für die Seitenzahl.

**Und eine Ungleichmäßigkeit, die dabei auffiel.** Der Abstand zwischen den
Knöpfen im Kopf wird jetzt an den anderen Knöpfen **gemessen** statt
festgeschrieben — und der Fluss-Knopf hatte einen eigenen Abstand von 2
Pixeln, ein Rest aus der Zeit, als er allein im Kopf stand. Alle anderen
Abstände kommen aus der Gruppe. Der Rest ist weg.

Ein Fehler war meiner: beim Ausreißen des Panels habe ich die **Hinweiszeile
mitgenommen**, die zwischen Panel und Verweis-Panel stand. 23 Prüfungen
meldeten daraufhin „kein Hinweis" — so viele, dass es eindeutig war.

Zwei Prüfungen kamen dafür dazu: die Trefferliste hängt unter dem Suchbereich
und ist genauso breit — vorher stand nirgends, dass „darunter" eine
Forderung war, sondern nur, dass sie irgendwo sichtbar ist.

**700 → 703 Prüfungen**, 23 Testdateien.

### `AGENTS.md`: was beim nächsten Mal wieder gewusst sein muss — und ein Knopf mit einem Zeichen

**`AGENTS.md` ist neu.** Sie sammelt das, was eine neue Sitzung nicht weiß
und nicht raten sollte:

- **vorher fragen**, wenn etwas mit dem MWS zu tun hat — der Austausch ist
  freigegeben, optische Änderungen auch, der Rest nicht
- **provisionieren** nach jeder Änderung, sonst sieht man nichts davon
- **nicht pushen**; committen ja, sobald ein Vorgang fertig ist
- **der Nutzer ist die Augen**: keine Screenshots, um eine Änderung zu
  prüfen. Statt eines Bildes die Zahl messen oder den Test schreiben, der
  sie festhält. Ausgenommen nur, wenn ein Aufbau-Problem die Ursache nicht
  erkennen lässt und kein Test es fassen kann
- **drei Fallen**, die in dieser Suite schon zugeschlagen sind: Headless
  nimmt kein Fenster unter 500 Pixeln; eine Position nach einer Transition
  ist dem Zufall überlassen; Headless-Chromium ist ein Snap und darf weder
  `/tmp` lesen noch dorthin schreiben
- **wie der Nutzer arbeitet**: er benennt Änderungen am Ergebnis, sagt nicht
  wie, und meldet sich, wenn etwas nicht passt

**Und der Knopf für eine neue Seite trägt jetzt nur noch ➕**, der Hinweis
drauf bleibt. Mit dem Wort waren es 116 Pixel, mit dem Zeichen 48 — der Kopf
passt dadurch bei 780 Pixeln wieder in **eine** Zeile, wo er vorher umbrach.

Dabei kam eine Ursache heraus, die nicht am Knopf lag: `.menu-toggle` trug
`margin-left: auto` und schob damit den ganzen Leerraum vor sich her. Der
Knopf für eine neue Seite — als erster in der Reihe — blieb allein beim
Suchfeld liegen, **372 Pixel** vor ☰. Die Knöpfe des Kopfs liegen jetzt in
einer Gruppe `.kopf-werkzeuge`, die den Leerraum gemeinsam schluckt. Der
Abstand zwischen ➕ und ☰ ist derselbe wie zwischen allen anderen.

Acht Tests suchten den Knopf **nach dem Text**. Mit einem Zeichen finden sie
ihn nicht mehr, und vier davon prüften „der Knopf ist weg" — die hätten
künftig **immer** bestanden. Sie suchen jetzt nach `.kopf-neu`, und der Name
steht als `title` und `aria-label` daran.

Und noch einmal die Transition, zum dritten Mal an derselben Stelle: der
Test maß die Breite der Spalte 900 ms nach dem Aufklappen. Beim vorigen Lauf
war die Fahrt schon fertig, beim ersten nicht. Der Test prüft jetzt den
Zustand und die CSS-Regel.

**700 → 701 Prüfungen**, 23 Testdateien.

### „Neue Seite" wandert in den Kopf, links neben das Verzeichnis — 700 Prüfungen

Eine Seite anlegen ist eine Tat, kein Ort. Der Knopf stand zwischen zwei
Zeilen, die man sich sonst ansieht, und er stand an der einen Stelle, an der
man ihn am wenigsten vermutet.

Er steht jetzt im Kopf, links von ☰, und im Fuß des Verzeichnisses steht
nur noch der Hinweis auf die Reihenfolge.

- Wie die anderen Schreibknöpfe **verschwindet er, wer nicht schreiben darf** —
  `t_anmeldung.py` prüft das am echten Server und war das ohnehin die
  Bedingung
- auf schmalen Fenstern **klappt der Text ein** und es bleibt ein „+", wie
  beim Fluss-Knopf daneben
- im Fuß des Verzeichnisses ist der untere Rand des Hinweises weg, der
  gehörte zum Knopf daneben

**Und zwei Fehler, die ich beim Umbau selbst gemacht habe.** Beide wären
ohne die Tests in die Wiki gegangen:

1. Das Plus stand doppelt da: „+ + Neue Seite". `t('newPage')` enthält es
   schon. Ein Test prüft die Zeichenkette nicht — dafür ist er nicht da.
   Bei der Messung stand es da.
2. `@click="createNewPage; closeAllPanels()"` — **ohne** Klammern ist in Vue
   eine Methode, die man ansieht und dann wegwirft. Aufgerufen wurde nichts,
   der Knopf tat gar nichts, und `t_mws.py` meldete nüchtern
   „erste neue Seite heisst Alpha". Jetzt mit Klammern.

`tests/t_kopf.py` prüft die Reihenfolge der Kopf-Knöpfe mit — sie ist jetzt
`neu toc fluss refs settings thema` — und dass der Knopf links neben dem
Verzeichnis sitzt. `t_fluss.py` prüft, dass im Verzeichnis kein Knopf mehr
steht, nur noch der Hinweis.

Eine Prüfung habe ich gleich mitgezogen, weil sie an der Headerhöhe hing:
`t_menue.py` verlangte „mehr als 400 Pixel hoch". Mit dem sechsten Knopf im
Kopf bricht der Kopf in eine zweite Zeile um, die Spalte wird 378 Pixel
hoch, und die Prüfung wird rot — an einem Umbau, den sie nicht meint.
Sie prüft jetzt „reicht bis zum Fuß". Eine feste Pixelzahl in einem Test
gilt immer nur für die Kopie des Tages.

**693 → 700 Prüfungen**, 23 Testdateien.

### Die Panels werden nicht mehr neben das Fenster geparkt, sondern auf seine Kante — 693 Prüfungen

Im Gerätemodus von Chrome (Galaxy S20 Ultra, 412 Pixel) war rechts ein
Streifen des Einstellungs-Panels zu sehen, **ohne dass jemand es geöffnet
hatte**. Das war seit dem ersten Tag so und stand seit zwei Tagen als
Beobachtung dabei — nicht, weil es harmlos war, sondern weil ich es nicht
zu Ende angesehen hatte.

Die Ursache ist eine Zahl im Stylesheet. Die Panels parkten mit
`right: -360px`: so weit rechts, wie sie breit sind. Das stimmt, solange sie
breit sind — und unterhalb von 768 Pixeln macht eine Media Query daraus
300 Pixel. Der Versatz blieb 360. Auf einem schmalen Fenster standen die
Panel damit 60 Pixel **im** Bild statt genau daneben.

Geparkt wird jetzt mit `translateX(100%)` — mit dem eigenen Maß des Panels.
Das hängt an keiner Zahl und damit an keiner Breite, und es gilt für jedes
Fenster, auch für eines, das morgen noch schmaler wird.

`tests/t_panels.py` prüft die Massgabe so, dass sie am alten Gesetz
gescheitert wäre: nicht „das Panel ist nicht zu sehen" (das galt vorher
auch), sondern „das Panel steht **genau** auf der Kante". Bei 500 Pixeln ist
das der Unterschied zwischen 765 und 780 — 15 Pixel, die Breite einer
Bildlaufleiste. Ein Panel steht an `right: 0` am Rand des **Layouts**, und
dort sitzt die Bildlaufleiste daneben, nicht darüber; `window.innerWidth`
zählt sie mit. Beides ist richtig, und man darf sie nicht verwechseln.

**Und dabei kam heraus, dass diese Suite seit langem lügt.** Chromium nimmt
kein Fenster unter 500 Pixeln:

```
--window-size=320   ->  innerWidth=500
--window-size=380   ->  innerWidth=500
--window-size=412   ->  innerWidth=500
```

`t_kopf.py` und `t_menue.py` wollten **380 Pixel** und haben **500**
gemessen. Beide fragten `innerWidth <= 560` — und 500 erfüllt das. Zwei Tests
waren grün und prüften etwas anderes als behauptet: das ist die Lehre aus
`tests/README.md`, eine Ebene tiefer, weil man sich das Fenster hier nicht
aussuchen konnte, ohne es zu bemerken.

Zwei Hebel wurden versucht und bringen nichts:
`--force-device-scale-factor` ändert `innerWidth` nicht, und die Wiki in
einen 380 Pixel breiten Rahmen zu setzen bringt nichts, weil dessen Timer
unter `--virtual-time-budget` nicht laufen. Einen Test, der so nicht
läuft, habe ich deshalb **nicht** geschrieben — lieber keiner als einer, der
nur so aussieht.

Was bleibt: Beide Tests **sagen es jetzt im Bildschirm**, statt eine Zahl zu
behaupten, und die Tatsache steht in `tests/README.md`. Das eigentliche
Verhalten bei 412 Pixeln muss auf einem Bildschirm geprüft werden — im
Gerätemodus von Chrome, wie es der Nutzer getan hat. Was sich prüfen lässt,
ist getestet: die Panels stehen bei **jeder** Breite auf der Kante.

Und noch eine Lektion, die dritte in Folge an derselben Stelle: nach dem
Anklicken wird die Lage eines Panels nicht gemessen. Es fährt 300 ms ein,
und unter Virtual Time steht die Fahrt am Anfang. Der Test prüft die Klasse
und die CSS-Regel.

**677 → 693 Prüfungen**, 23 Testdateien.

### Auf einem schmalen Fenster fängt das Verzeichnis zugeklappt an — 677 Prüfungen

Das Verzeichnis stand auch dann offen, wenn es mehr als die Hälfte des
Fensters wegnahm: bei 420 Pixeln waren das 300 Pixel Verzeichnis und 120
Pixel Text.

Ab einer Fensterbreite von **640 Pixeln** fängt es deshalb zugeklappt an.
Die Zahl ist eine Rechnung und keine Empfindung: unterhalb von 768 Pixeln
wird das Verzeichnis 300 Pixel breit, und bliebe es offen, käme der Text auf
weniger als 340 Pixel — schmaler als die Spalte auf einem Telefon. Man kann
es lesen, aber es ist kein Lesen mehr.

Die Grenze steht als `TOC_MENUE_OFFEN_BIS` an **einer** Stelle im Programm,
und `t_menue.py` prüft das nach — die Grenze selbst im Browser, und dass sie
an genau einer Stelle steht und nirgends gespeichert wird, in der Datei.

**Nur beim Start.** Wer das Verzeichnis zuklappt, hat das so entschieden, und
das gilt auch, wenn das Fenster danach schrumpft. Ein Menü, das sich beim
Ziehen selbst umstellt, ist eines, dem man nicht traut.

Nachgemessen: 600 Pixel → zu, 660 Pixel → offen mit 300 Pixel Spalte,
900 Pixel → offen mit 360 Pixel.

**669 → 677 Prüfungen.**

### Drei Zeilen raus: das Menü gehört zur Seite und nicht in eine Karte — 669 Prüfungen

Drei Angaben, die das Menü wie eine Karte aussehen ließen, sind weg.

- `background: var(--bg-secondary)` an `.toc-menu` — das Menü bekommt keinen
  eigenen Grund mehr. Es hat denselben wie die Seite, und das ist der ganze
  Punkt: es ist ein Teil der Seite, kein Kasten daneben.
- `border-right: 1px solid var(--border-color)` an `.toc-menu` — keine
  Trennlinie. Die Kante zwischen Verzeichnis und Infall sagt das Fähnchen,
  und die steht genau dort.
- `border-bottom: 1px solid var(--border-color)` an `.side-header` — auch
  keine Linie unter „Inhaltsverzeichnis".

Dazu eine vierte, die niemand verlangt hat und die von selbst mitfällt: der
Menükopf hatte `background: var(--bg-primary)`. Den gab es nur, um die
vorherige Kartenfarbe wieder zu überschreiben. Ohne Karte ist er nichts, was
man sehen könnte.

`.side-header` ist eine gemeinsame Klasse — sie hängt auch am Verzeichnis-
und Verweis- und Einstellungs-Panel rechts. Die drei Panels verlieren ihre
Trennlinie unter der Überschrift mit. Das ist die Kehrseite und vermutlich
genau richtig: es sind dieselben Panels, und eins sah aus wie die anderen.

Im Hellen wie im Dunklen nachgesehen und am PDF gegengeprüft. 669 Prüfungen.

### Das Menü ist eine Spalte, kein Overlay — 669 Prüfungen

Der erste Versuch legte sich vor den Inhalt. Zwei Beschwerden kamen zurück:
das Menü verdeckte die Kopfzeile, und es drängte nichts zur Seite.

Eine Overfläche kann das nicht. Sie liegt über allem und wird nur
dazugestellt — und wenn daneben nichts Platz ist, verschwindet Inhalt
hinter ihr, statt zur Seite zu rücken.

Also ist es jetzt eine **Spalte im Aufbau**. Der Körper der Wiki ist eine
Zeile aus zwei Teilen: links das Verzeichnis, rechts der Inhalt. Das Menü
ist ein Flex-Kind und nicht mehr `position: fixed`. Damit kommt von selbst,
was gefordert war:

- es **beginnt unter der Kopfzeile** — die ist ein eigenes Flex-Kind über
  der Zeile, und ihre Höhe ist ihr eigener, nicht unsere
- es **drängt den Inhalt nach rechts** — es nimmt Platz im Aufbau, statt zu
  überdecken. Wer es zuklappt, gibt den Platz wieder her, und der Text rückt
  nach links
- es **verdeckt nichts** — kein Punkt, kein Absatz, keine Taste liegt
  hinter ihm

Dazu die Kleinarbeiten, die ein Umbau mit sich bringt:

- `min-width: 0` an der Inhaltsspalte. Ohne das weigert sich ein Flex-Kind,
  schmaler zu werden als sein Inhalt, und die Spalte bliebe breit.
- `min-height: 0` am Körper, damit der Rollbalken im Fluss greift
- `max-width: 85%` am Menü und `min(var(--toc-breite), 85%)` am Fähnchen:
  auf einem 320-Pixel-Fenster soll nicht die ganze Wiki unter dem Verzeichnis
  verschwinden
- Der Körper steht im Druck mit auf `display: block` und
  `height: auto`, sonst sähe das Papier eine Zeile mit zwei Spalten

**Und ein Fehler, den erst die zweite Liste aufgedeckt hat.** `onZeileKeydown`
nahm die Zeile, auf der der Fokus landen soll, aus dem **ganzen Dokument**:
`document.querySelectorAll('.toc-item')[ziel]`. Mit einer Liste stimmt das.
Mit zweien liegen sie nebeneinander, und nach einem Alt+Pfeil im Panel rechts
sprang der Fokus in die Liste links — man drückt an einer Stelle und tippt an
einer anderen. Die Zeile hält sich jetzt ihre Liste, aus der sie gedrückt
wurde, und `t_menue.py` prüft das für beide.

**Und noch eine Lektion, die ich mir gerade selbst gegeben hatte.** Der erste
Versuch des Tests maß die Breite der Spalte kurz nach dem Zuklappen — genau
die Sache, vor der die Lehre in `tests/README.md` warnt. Zweimal rot, ohne
dass etwas kaputt war. Der Test prüft jetzt den Zustand und die CSS-Regel,
nicht die Mitte einer 250-ms-Fahrt.

**660 → 669 Prüfungen.** Am PDF gegengeprüft: keine Kopfzeile, kein Fähnchen,
keine Taste — und der Text steht am linken Rand.

### Das Inhaltsverzeichnis wird ein Menü, und das Löschkreuz verschwindet — 660 Prüfungen

Zwei optische Änderungen, beide in `simplewiki.html`.

**1. Kein Löschkreuz mehr im Verzeichnis.** Es stand eine Zeile entfernt vom
Löschen einer ganzen Seite, mit einem Dialog dazwischen, der nach einem
Versehen trotzdem wegklickt. Gelöscht wird jetzt nur noch dort, wo man es
gerade tut: im Editor, neben Bearbeiten und Speichern, mit Abbrechen daneben.

**2. Das Verzeichnis steht links als Menü.** Vorher musste man es erst über
☰ aufmachen — ein Verzeichnis, das man sich suchen muss, ist keines. Es ist
jetzt beim Öffnen da und fährt am **Fähnchen** an der Innenkante weg und
wieder heran. Kein Overlay: es dunkelt nichts ab, ein Klick daneben wirft es
nicht zu, und wenn man darin eine Seite wählt, bleibt es offen. Ein Menü
verhält sich so.

Das Panel rechts (☰) bleibt, wie es war, mit allem was darin war — die Liste
steht jetzt an zwei Orten. Das ist gewollt: das Menü ist der bequeme Weg,
das Panel rechts der Ort, an dem die Suche steht.

- dieselbe Breite wie das Panel rechts, an einer Stelle als `--toc-breite`
  festgelegt, damit Menü und Fähnchen nicht auseinanderlaufen können; das
  Fähnchen rechnet sogar in sehr schmalen Fenstern mit (`min(…, 90vw)`)
- `side-panel` bleibt dran — damit erbt das Menü die Druckregel und
  verschwindet auf Papier, wie die anderen Panels
- Fähnchen mit `title`, `aria-label` und `aria-expanded`, beide Richtungen
  übersetzt (deutsch und englisch)
- Der Zustand gilt nur für dieses eine Fenster. Er wird nicht gemerkt: wer es
  zuklappt, will es auch beim nächsten Mal aufgeklappt haben.

`tests/t_menue.py` prüft das nach — und steckt dabei zweimal den Finger in
eine Wunde, die schon im Haus war:

> **Eine Position nach einer Animation ist dem Zufall überlassen.** Die
> Transition fährt 300 ms, und unter Virtual Time läuft die Animationsuhr
> nicht zuverlässig mit den Timern des Testskripts. Der erste Versuch des
> Tests hat genau daran zweimal rot gemeldet, ohne dass etwas kaputt war.
> Gemessen wird jetzt nur dort, wo noch nichts gefahren ist; die *Wirkung* des
> Zustands wird an der Klasse und an der CSS-Regel geprüft.

Weil die Liste nun zweimal im Dokument steht, zählt in den Tests jedes
`.toc-item` doppelt. Wo ein Test zählt oder vergleicht, schreibt er jetzt
`.toc-panel` davor — das Panel rechts, der Ort, den diese Tests seit jeher
beschreiben. Zwei Löschtests gingen vorher über das Kreuz im Verzeichnis und
löschen jetzt über den Editor; im Zuge dessen kam ein Fehler in `t_suite.py`
zum Vorschein, wo beim Umbau zwei Klammern zu viel geschlossen waren — der
Test meldete daraufhin „KEIN REPORT" statt einer Zahl.

**621 → 660 Prüfungen.**

### Tests, die nicht liefen — 621 Prüfungen statt 539

Drei Dateien haben der Suite Arbeit gemeldet, die sie nicht geleistet haben.
Drei Fehler derselben Art, alle gefunden beim Nachsehen auf eine Zahl, die
nicht aufging.

**Ein Test, der nie läuft, ist grün.** `pruefe()` beendet das Skript. In
`t_kopf.py` stand der Aufruf für die Kopie mit dem schmalen Fenster **hinter**
dem `sys.exit` — die Prüfungen liefen, ihre sechs Ergebnisse waren aber weder in
der Zahl noch im Exitcode. `_kopf2.html` konnte nicht mehr rot werden.

**Und derselbe Fehler ein drittes Mal, mit mehr Schaden.** In `t_leerwiki.py`
stand `pruefe(kopie1, kopie2)` hinter demselben `sys.exit`: **Teil 1 lief nie** —
die 13 Prüfungen für die oberen Fremdfelder (`autor`, `herkunft`, `exportdatum`),
also genau der Weg, den ein Kind geht, wenn es ein fremdes JSON einliest und
zurückgibt.

**Eine Prüfung ohne Zahl ist eine Prüfung ohne Wirkung.** `alle.py` zählt nur,
was als `GESAMT: N bestanden, M fehlgeschlagen` dasteht. Drei Skripte zählten
ihre Fehler, meldeten aber keine bestandenen Prüfungen und trugen deshalb zur
Gesamtzahl **null** bei — bei laufenden Prüfungen.

Dazu eine Kleinheit in `t_abnahme.py`: `melde()` hat einen durchgefallenen
Abnahmepunkt **sowohl als bestanden als auch als fehlgeschlagen** gezählt.

Behoben:

- `pruefe()` kann jetzt ein Fenster je Kopie bekommen (`fenster=`) und Fehler
  aus den vorangegangenen Teilen eines Skripts mitrechnen (`schon_fehler=`) —
  damit wieder ein Aufruf am Ende alles zusammenführt, statt am Skript-Ende
  zu stehen und dort zu sterben
- `_kopf2.html` und `_weg1.html` laufen durch denselben Weg wie der Rest und
  zählen mit
- `t_export.py` und `t_fluss.py` melden eine `GESAMT:`-Zeile
- in `t_kopf.py` stand `>>> 0 FEHLGESCHLAGEN || ALLE BESTANDEN` — `0` ist in
  JavaScript ein wahrer String, der Ausweichzweig griff nie

Geprüft, dass es wirkt: ein absichtlich scheiternder Test mit schmalem Fenster
macht den Lauf rot und nennt die Prüfung.

**539 → 621 Prüfungen.** Die 82 dazugekommenen sind keine neuen Prüfungen,
sondern längst vorhandene, die nie stattgefunden haben.

### `README.md` und `CHANGELOG.md`

Was fehlte, ist jetzt da.

- **`README.md`** — was das ist, wie man loslegt, wie `simplewiki.html`
  aufgebaut ist (mit Zeilennummern), die zwei Betriebsarten, das
  Austauschformat, der Provisionier-Schritt, die Tests, die eingebetteten
  Bibliotheken mit Lizenz und Version, und die Grenzen, die Absicht sind.
- **`CHANGELOG.md`** — alles, was seit der ersten Fassung gebaut wurde, nach
  Tag, mit der Prüfungszahl des damaligen Stands. Nachgeschrieben aus den
  Commit-Nachrichten, nicht erfunden.
- **`tests/README.md`** nachgezogen: die vier Testdateien fehlten in der
  Übersicht, `pdfinfo`/`pdftotext` fehlten als Abhängigkeit, und der Satz
  „ein Test steht nicht in `alle.py`“ leading zu einem Missverständnis.

Suite zur Zeit des Schreibens: **621 Prüfungen, 0 fehlgeschlagen**, 21
Testdateien.

### Anmelden führt zurück in die Wiki, aus der man kam — 539 Prüfungen

Der Anmelde-Link trägt den Weg, von dem man kommt, als `redirect`-Parameter mit:
`/login?redirect=/wiki/<name>`. Ohne das schickt MWS nach dem Anmelden auf die
Startseite, also auf eine Liste von Konten — wer in einer Wiki auf „Anmelden“
klickt, will danach wieder in dieser Wiki sein und nicht auf einer.

Nimmt der Server den Parameter nicht, ist das **kein Fehler**: man landet auf
der Startseite, also auf dem Weg von vorher.

### Anmelden und abmelden — 538 Prüfungen

- **Anmelden ist ein Link**, kein Knopf mit Rumpeln: es ist ein Link auf
  `/login` mit `title`, damit mittlere Maustaste, Tab und der Link im
  Statusfenster alle so tun, wie man es erwartet.
- **Abmelden geht von hier aus** (`⎋` neben dem Namen), weil es nichts zu
  beweisen gibt: es muss nur eine Sitzung ungültig gemacht werden. Danach wird
  `/status` neu geholt, und was der Server sagt, entscheidet — nicht, was
  gerade noch angezeigt war. Stimmt der Kopf also auch dann, wenn die Sitzung
  schon vorher abgelaufen war.
- **Scheitert das Abmelden, wird es gesagt** — und nichts angezeigt, was nicht
  wahr ist. Eine Abmeldung, die nicht stattgefunden hat, darf nicht aussehen
  wie eine.
- **Kein Passwortfeld in der Wiki.** MWS prüft es mit OPAQUE; die Bibliothek
  dafür lädt diese Wiki bewusst nicht (siehe *Grenzen* in der `README.md`).
- Jeder Schritt bekam einen **eigenen Server**: die Sitzung gehört dem Server,
  nicht dem Browserfenster.

### Merksatz: nach jeder Änderung provisionieren

```bash
npm start provision-simplewiki <pfad>/simplewiki.html
```

Die Wiki liest ihre Schale **aus dem Store**, nicht aus `simplewiki.html`. Ein
Neustart des Servers ändert daran nichts — der Server liest dieselbe alte
Schale aus demselben Store.

Genau das ist an diesem Tag passiert: eine Änderung war Stunden fertig und
getestet (495 Prüfungen grün, der Live-Check gegen das echte MWS ebenfalls) —
und in der laufenden Instanz war **nichts davon zu sehen**. Der Beutel des
Templates war vom Vorabend, die neue Datei nirgends eingelesen. `live_mws.py`
macht den Schritt von selbst, deshalb sah sein Lauf gut aus; der Test allein
hätte aber nicht geholfen.

Der Satz steht jetzt im README, gleich vor der Beschreibung des Live-Checks —
weil man genau dort sucht, wenn die Wiki im Browser anders aussieht als im
Test.

### Anmeldung: der Name steht im Kopf, Schreibtasten nur mit Recht — 495 Prüfungen

Gefragt war die erste Frage schlicht: **unter welchem Namen bin ich
angemeldet**. Die App wusste es nicht. Sie wusste nur, dass ihr ein
Schreibversuch mit 403 beantwortet wurde, und bis dahin standen alle Tasten da,
nur grau.

- `GET /recipe/<name>/status` wird beim Start geholt und beantwortet vier
  Zustände: **niemand angemeldet**, **angemeldet ohne Recht**, **angemeldet mit
  Recht**, **Sitzung abgelaufen**.
- Die **Schreibknöpfe sind nicht abgeschaltet, sondern weg.** Wer nicht schreiben
  darf, soll gar nicht erst auf einen Knopf zeigen, der ohnehin nichts tut.
- Ein **Ausfall ist kein Rechteproblem**: antwortet der Server nicht, wird
  nichts erfunden — kein Nur-Lesen-Zustand, keine verlorenen Knöpfe.
- Läuft die Sitzung **mitten drin** ab, schaltet die App beim nächsten
  Schreibversuch um, ohne Neuladen.

---

## 2026-10-04

### B3: aus der leeren Wiki gibt es jetzt einen Ausgang — 455 Prüfungen

Die leere Wiki war eine Sackgasse: nirgends war ein Ausgang. Der Leerzustand
bekommt jetzt einen Knopf, der die erste Seite anlegt und den Editor öffnet.
Wer nicht schreiben darf, bekommt ihn nicht zu sehen.

### B2: der Tiddler heißt wie die Seite — 445 Prüfungen

Ein Tiddler heißt nach seinem Inhalt, wie es die TiddlyWiki-Konvention vorgibt —
der Vertrag im Kopf der Wiki wurde entsprechend festgeschrieben. Die stabile
Kennung wandert als Feld `sw-id` mit, damit die Seite beim Umbenennen dieselbe
bleibt; ein Tiddler ohne `sw-id` — von MWS oder von einem Menschen angelegt —
liefert seine Kennung aus dem Titel.

Ergänzung an der Oberfläche: ein Feld `reihenfolge`, vierstellig. TiddlyWiki
kennt keine Reihenfolge von Tiddlern, SimpleWiki schon — ohne dieses Feld wäre
sie nach dem Neuladen weg.

### B1: der Marker existiert jetzt wirklich — 435 Prüfungen

Der Punkt im Dokument, hinter dem MWS seine Tiddler einsetzt, stand als
Zeichenfolge **im Kommentar**, der ihn erklärt. MWS sucht wörtlich und nimmt
den ersten Fundort im Dokument — auch einen in einem Kommentar. Die Wiki
stünde schön und leer da, und jede Eingabe landete im Browser und wäre beim
nächsten Aufruf weg. Der Text kommt jetzt genau einmal vor, auf den Roh-Bytes.

### Abnahme: die fünf Punkte als nachlesbarer Test — 430 Prüfungen

Aus der Abnahme wurde `tests/t_abnahme.py`. Fünf Punkte, jeder mit benannten
Prüfungen:

1. **kein Nachladen** — kein `<script src>`, kein `<link rel=stylesheet>`, kein
   `@import`, keine `http(s)://`-Referenz, jede `url()` in den `<style>`-Blöcken
   ist `data:`
2. **die Suite ist grün** — das macht `tests/alle.py`, nicht diese Datei
3. **Doppelklick ohne Netz** — der alte `localStorage`-Zustand schlägt den
   Dateiinhalt
4. **mit injiziertem Store erscheint der Inhalt in der Oberfläche**
5. **eine Änderung ist nach Neuladen wieder da**

### Tests für die MWS-Auswahl und die Verweise — 413 Prüfungen

- **`tests/mwsfixture.py`** baut eine Datei, die so aussieht, als käme sie vom
  MWS: der Marker an die echte Head-Grenze, Testskripte wie `mkcopy` es für
  Dateikopien macht. `mwsserver.py` benutzt dieselbe Funktion — es gibt also
  nur noch **eine** Stelle, die weiß, wie ein Server auszusehen hat. Die
  Fixture wird **erzeugt und nicht gespeichert**: eine mitgecheckte Kopie von
  `simplewiki.html` wäre bei der nächsten Änderung still veraltet, und niemand
  merkt es, bis ein Test etwas anderes prüft als gedacht.
- **`tests/t_mwsdatei.py`** prüft die Auswahl am Marker in vier Durchgängen:
  Marker mit Inhalt (Server liefert), Marker leer (Browser liefert — auch wenn
  die Datei vom Server kommt), gar kein Marker (die gewöhnliche Datei) und
  Schreiben aus einer Datei.
- Der letzte Fall ist der ehrliche: aus einem Doppelklick heraus gibt es keinen
  Server, also schlägt der Schreibversuch fehl. Wichtig ist nur, dass er
  **sichtbar** scheitert — und dass nicht so getan wird, als wäre die Wiki nur
  lesbar.
- Dabei kam ein Fehler heraus, der nichts mit MWS zu tun hatte und deshalb
  lange unentdeckt war: **marked lässt eine URL mit Leerzeichen nicht als Link
  gelten.** `[Text](wiki:Zweite Seite)` blieb reiner Text, der Verweiszähler
  erkannte dieselbe Stelle aber sehr wohl. Die App widersprach sich selbst: im
  Verweispanel stand der Link, in der Seite stand Text. `ersetzeWikiSyntax()`
  zieht jetzt auch die schon geschriebene Form durchs properpe Verfahren und
  macht daraus `encodeURIComponent`. Da der Schritt nur beim Anzeigen läuft,
  wird am Text nichts geändert, der zum Server geht.
- **Drei Versuche statt zwei**, bevor ein Test als gescheitert gilt. Die Suite
  arbeitet dutzende Browserläufe ab, und zweimal unter Last durchfallen war
  häufig genug, dass ein roter Lauf nichts mehr bedeutet hätte.

### Tiddler und Seite: das Mapping an seinen Ecken geprüft — 394 Prüfungen

Zeitstempel mit 17 Stellen, Tags mit Leerzeichen und Emoji, doppelte Tags,
Tiddler ohne `sw-id`, Systemtiddler, `created` von einem 14-stelligen Wert, das
app-Feld `content` gegen das Tiddler-Feld `text`.

### MWS-Schnittstelle: Fehler sichtbar, `list` und `read` — 380 Prüfungen

Antwortet der Server mit 500, steht der Grund im Hinweis — und es wird **kein
Nur-Lesen-Zustand erfunden**. „Ein Ausfall ist kein Rechteproblem.“

### Speicher: eine Abstraktion, zwei Ausprägungen — 368 Prüfungen

`laden`, `uebernehmen`, `seiteSichern`, `seiteLoeschen`, `startseiteSetzen`,
`themaSetzen`, `spracheSetzen` — sieben Methoden, die der Rest des Programms
kennt und der Rest nicht unterscheidet. Zwei Ausprägungen: `LocalStore` und
`MwsStore`. Geprüft wird nicht nur, dass beide sie haben, sondern dass die
laufende App sie wirklich benutzt.

### MWS-Betrieb: Seiten liegen auf dem Server — 338 Prüfungen

Zwölf Wiki-Zustände gegen einen Testserver: Reihenfolge aus dem Store, Tiddler
ohne Kennung, Startseite aus `$:/DefaultTiddlers`, Dunkelmodus und Sprache aus
den Feldern der Startseite, 403 bei fehlendem Schreibrecht, Store leer →
Browser gewinnt, Server kaputt → Hinweis statt Rechtebehauptung.

### Bibliotheken einbetten: kein CDN mehr — 302 Prüfungen

Vue, marked und TOAST UI stecken fest in der Datei statt von einem CDN zu
kommen. Eine strikte Content-Security-Policy erlaubt nur `self`, und eine Wiki
soll auch ohne Netz laufen.

### Aus dem Inhaltsverzeichnis: nur noch der Druck-Knopf

Im Fluss bleiben Kopfzeile, Suche und Einstellungen stehen; im
Inhaltsverzeichnis verschwindet der Fluss-Knopf, damit er nicht an zwei Orten
auftaucht. Abstand zu den Seitenrändern, wie man ihn beim Lesen erwartet.

### Fluss-Knopf in den Kopf

Der Fluss wird aus dem Inhaltsverzeichnis in die **Kopfzeile** verschoben: ein
Knopf, eine Wirkung, und er ist auch erreichbar, wenn das Inhaltsverzeichnis
zu ist. Geprüft wird auch die **Reihenfolge der Knöpfe im Kopf**
(`toc · fluss · refs · settings · thema`) und dass alles davon in einem Fenster
mit 380 Pixeln Breite noch passt.

### Exportweg fertig: Fremdangaben oben, leere Vorlage, Vertrag

- **Fremdangaben** auf der obersten Ebene (`autor`, `herkunft`, `exportdatum`)
  überstehen einen Hin-und-Her-Weg.
- **Leere Vorlage** (`simplewiki-leer.html`) zum Füllen für ein anderes
  Programm — nicht zum Laden: eine Datei ohne Seiten wird abgelehnt, sonst
  ersetzt ein missglückter Export die ganze Wiki.
- **Fremde JSON-Datei laden** und als Wiki-Datei weitergeben.

### Lesebreite in der Seitenansicht wie im Fluss

Die Textspalte war nur im Fluss begrenzt (860px); die normale Seitenansicht
lief über die volle Fensterbreite. Jetzt ist **beide gleich breit**, damit eine
Seite und ihre Nachbarin im Fluss gleich aussehen.

- `--spaltenbreite` als CSS-Angabe an genau einer Stelle, damit die beiden
  Ansichten nicht auseinanderlaufen können
- die Begrenzung sitzt auf den **Kindern** von `.content-body` und nicht auf
  `.content-body` selbst: der Scrollbalken bleibt am Fensterrand statt bei der
  Spalte zu stehen
- seitliches Polster im Fluss gestrichen — es hat den Text dort noch 40px
  schmaler gemacht, deshalb passten die Breiten trotz gleicher Zahl nicht
  wirklich zusammen

**Gemessen statt geschätzt:** 860px in beiden Ansichten.

Dabei kam ein Nebenschaden heraus, den ein bloßes Anschauen nicht gezeigt
hätte: die Kopfzeile ist ein Flex-Kind und schrumpfte mit den automatischen
Rändern auf 57px — der Trennstrich unter dem Titel war nur noch kurz. Sie
bekommt jetzt `width: 100%`.

### Austausch mit MWS: JSON, Version, fremde Felder

Das Austauschformat steht jetzt im Kopf der Datei, als Kommentar, der
beides ist: die Doku und der Vertrag. Drei Zusagen, die ein Test prüft —
JSON und HTML gleichwertig, fremde Felder bleiben, zu neue Dateien werden ganz
abgelehnt.

Zwei Entscheidungen, die nicht in der Vorgabe standen: eine Datei **ohne
Seiten** wird abgelehnt statt als leeres Wiki übernommen, und beim **Anlegen**
wird ein vergebener Name still eindeutig gemacht, beim **Umbenennen** wird
abgelehnt und der Name genannt.

### Fluss: scrollbar und Druck über mehrere Seiten

Der Fluss ließ sich in einem kurzen Fenster nicht scrollen, und der Druck
verlor alles nach Bildschirmhöhe. Beides fiel nur auf, weil der Test mit einem
Fenster von 900×420 Pixeln und absichtlich langen Seiten prüft — und weil am
Ende nicht nur „sieht vollständig aus“ steht, sondern der letzte Satz der
letzten Seite wirklich im ausgelesenen PDF.

### Sichern: die Datei behält ihre Oberfläche

Die gesicherte Datei ist dieselbe Datei: dieselbe Oberfläche, dieselben
eingebetteten Bibliotheken, nur die Dateninsel ist gefüllt. Ein
`<script>` im Seiteninhalt übersteht das als `</script` in der Datei.

### Reihenfolge per Ziehen ändern und das Wiki als Datei sichern

Griff ⠿ zum Ziehen, **Alt + Pfeiltaste** als zweiter Weg für die Tastatur, und
ein Hinweis, der beide nennt. Während der Suche ist die Reihenfolge gesperrt —
und der Hinweis sagt, warum.

### Verweise als eigenes Panel

Rück- und Ausgehende mit Zähler im Kopf, mit `→` und `←`, fehlende Ziele als
`?` mit der Möglichkeit, sie anzulegen. Der Zustand (offen oder zu) überlebt
das Neuladen.

### TiddlyWiki-Syntax `[[Seite]]` und `[[Text|Seite]]` verlinken

Innerhalb von Code ist `[[…]]` kein Verweis, sondern Beispieltext.

### Tests ins Projekt holen, bevor `/tmp` sie wegwischt

Die 224 Prüfungen lagen in `/tmp/opencode` — beim nächsten Neustart wären sie
weg, und gerade **sie** haben mehr gerettet als meine Vorsicht. Sie liegen jetzt
unter `tests/` und werden mitversioniert.

```bash
python3 tests/alle.py          # alles
python3 tests/alle.py fluss    # nur ein Teil
python3 tests/t_order.py       # ein einzelner Test
```

Endecode 0 heißt: alles bestanden.

- Pfade sind relativ, der Ordner darf liegen, wo er will
- Kopien, PDFs und Bilder landen in `tests/_kopien/` und werden nicht committet
- `mkcopy.py` setzt `localStorage` vollständig zurück; vorher schleppte ein
  Testlauf seinen Zustand in den nächsten — daher kam das Verweis-Panel
  manchmal schon offen herein
- README mit der Übersicht und zwei Lehren aus den Tests

Zwei Fehler beim Umstellen gefunden und behoben: durch das Zusammenfassen der
`build`-Aufrufe kam die Zustandsvorgabe auch in die erste Kopie, und eine
Prüfung erwartete noch „nichts gespeichert“, obwohl der Seed inzwischen
bewusst einen Wert schreibt.

---

## 2026-10-03

### Seiten duplizieren

Der ⧉-Knopf legt eine Kopie mit eigenem Namen an. Sie bekommt **eigene
Kennung, eigene Verknüpfungen** — ein Link in der Kopie zu entfernen fasst die
Vorlage nicht an.

### Seiten verlinken: Verknüpfungen und Rückverweise

Der Verweis auf eine andere Seite steckt in den **Seiten-Metadaten**
(`page.links`), nicht im Markdown-Text: die direkte Schreiboperation in den
Toast-Editor scheitert unter `file://` mit
`RangeError: Applying a mismatched transaction`.

- Link-Dialog im Bearbeitungsmodus: Seiten verknüpfen und lösen, nicht
  vorhandene Seiten werden dabei angelegt
- Abschnitt „Verlinkt auf“ mit den Zielen und „Verlinkt von“ mit den
  Rückverweisen
- der Leer-Zustand hängt an `v-if="!currentPage"` und wird deshalb **nur**
  gezeigt, wenn es wirklich keine Seite gibt

### SimpleWiki: erste Fassung als einzelne HTML-Datei

Oberfläche, Editor, Markdown, Speicher im Browser und alle Bibliotheken in
**einer** Datei. Kein Server, kein Build, keine Installation: wer die Datei
doppelklickt, hat ein Wiki; wer sie weiterreicht, gibt ein Wiki weiter.