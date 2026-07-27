D# Figma MCP Design-Context: Node `78:725`

## 1. Ausgangsanfrage

Der Nutzer hat folgenden Prompt mit einer Figma-URL übergeben:

> Implement this design from Figma.
> `https://www.figma.com/design/isyoakVzVVVEsS6lHxnbzP/Untitled?node-id=78-725&m=dev`

Zusätzliche Nutzerabsicht:

> Ich interessiere mich für den Request und die Informationen die du bekommst und extrahierst. Bitte Liste mir alles auf. Ich möchte eine sequentielle textuelle Beschreibung von dem haben was du gleich tust.

Die tatsächliche Arbeitsabsicht war damit: den Figma-Design-Context lesen, den Request und die Rückgabe transparent dokumentieren und noch keinen Code im Projekt verändern.

## 2. Aus der URL extrahierte Figma-Parameter

| Parameter | Wert |
|---|---|
| Figma-Datei / `fileKey` | `isyoakVzVVVEsS6lHxnbzP` |
| Zielknoten / `nodeId` | `78:725` |
| URL-Notation des Node | `78-725` |
| Dateiname im Link | `Untitled` |
| URL-Pfad | `/design/` |
| Query-Parameter | `node-id=78-725`, `m=dev` |

Die Bindestrichschreibweise aus der URL wurde gemäß Figma-MCP-Konvention in die Node-ID `78:725` umgewandelt.

## 3. Zielprojekt-Kontext

Vor dem MCP-Request wurde der Workspace lesend geprüft. Er enthält unter anderem:

- Django-Backend mit `backend/manage.py`, `backend/config/` und `backend/editor/`.
- Django-Templates unter `backend/editor/templates/editor/`.
- CSS unter `backend/editor/static/editor/`.
- JavaScript-Komponenten, unter anderem `tableEditor.js`.
- Vorhandene Design-Token-Datei `backend/editor/static/editor/css/tokens.css`.

Daraus wurden für das Logging des Design-Context-Requests folgende Client-Angaben verwendet:

- `clientFrameworks`: `django`
- `clientLanguages`: `python,html,css,javascript`

## 4. Exakter Request an `get_design_context`

Der lesende Figma-MCP-Request wurde mit folgenden Parametern ausgeführt:

```json
{
  "fileKey": "isyoakVzVVVEsS6lHxnbzP",
  "nodeId": "78:725",
  "clientFrameworks": "django",
  "clientLanguages": "python,html,css,javascript",
  "skillNames": "figma-design-to-code"
}
```

Nicht gesetzt wurden:

- `disableCodeConnect`: nicht gesetzt; Code Connect blieb aktiviert.
- `excludeScreenshot`: nicht gesetzt; der Screenshot wurde angefordert.
- `forceCode`: nicht gesetzt; der MCP durfte bei Bedarf auf Metadaten ausweichen.

## 5. Sequenz der tatsächlich ausgeführten Aktionen

1. Die Figma-Design-to-Code-Anleitung wurde gelesen. Sie schreibt vor, vor dem Auslesen eines Designs zuerst `get_design_context` zu verwenden und den gelieferten Code nur als Referenz zu behandeln.
2. Der Workspace wurde lesend auf Stack, Dateien, Templates, Styles und Tokens geprüft.
3. Die URL wurde in `fileKey` und `nodeId` zerlegt.
4. Der erste `get_design_context`-Request wurde an den Figma-MCP gesendet.
5. Der Request war erfolgreich. Die Konsolenausgabe war wegen der Größe der Rückgabe abgeschnitten.
6. Deshalb wurde derselbe lesende Request ein zweites Mal ausgeführt, um die Antwort strukturiert zu vermessen und vollständig auszuwerten. Das war kein Fehler-Recovery-Retry, sondern ein Auswertungsrequest.
7. Die Antwort wurde in einzelne Content-Blöcke zerlegt: Referenzcode, Umsetzungshinweise, Node-ID-Hinweis, Design-Tokens, Asset-Hinweis und Screenshot.
8. Die Textblöcke wurden vollständig ausgelesen; der Screenshot wurde als empfangener Bildblock erfasst.
9. Es wurde noch keine Projektdatei verändert und kein Figma-Schreibrequest ausgeführt.
10. Diese Markdown-Datei dokumentiert Request, Rückgabe, Extraktion und den vorgesehenen nächsten Implementierungsablauf.

## 6. Antwort-Metadaten

Beide Requests waren erfolgreich (`isError: false`). Die MCP-Request-IDs waren:

- Erster Request: `d2ffd8ac-3d14-44c5-8eba-edde5e4a29c4`
- Zweiter Auswertungsrequest: `77d39975-627d-4e5c-8eba-edde5e4a29c4`

Die zweite strukturierte Antwort enthielt sechs Content-Blöcke:

| Index | Typ | Umfang / Inhalt |
|---:|---|---|
| 0 | `text` | 20.475 Zeichen React+Tailwind-Referenzcode |
| 1 | `text` | 551 Zeichen kritische Stack-/Styling-Hinweise |
| 2 | `text` | 83 Zeichen Hinweis zu `data-node-id` |
| 3 | `text` | 396 Zeichen Design-Tokens und Stile |
| 4 | `text` | 354 Zeichen Asset- und Ablaufhinweise |
| 5 | `image` | PNG-Screenshot, 165.468 Zeichen Bilddaten/Base64 |

Der Screenshot wurde empfangen, aber nicht in diese Datei kopiert, weil es sich um einen großen Binär-/Base64-Block handelt. Seine MCP-Metadaten waren:

```text
type: image
mimeType: image/png
dataLength: 165468
```

## 7. MCP-Hinweise aus der Antwort

### 7.1 Stack und Styling müssen angepasst werden

Der MCP weist ausdrücklich darauf hin, dass der generierte React+Tailwind-Code **nicht direkt** als fertiger Projektcode verwendet werden darf. Vorgesehen ist:

1. Zielprojekt auf Technologie-Stack, Styling, Komponenten-Muster und Design-Tokens analysieren.
2. React-Syntax in das Ziel-Framework beziehungsweise die Zielbibliothek übertragen.
3. Tailwind-Klassen in das vorhandene Styling-System übersetzen und dabei das visuelle Ergebnis erhalten.
4. Vorhandene Projekt-Konventionen befolgen.
5. Tailwind nicht als neue Dependency installieren, außer der Nutzer fordert das ausdrücklich.

### 7.2 Node-IDs im Referenzcode

Der zurückgelieferte Code enthält `data-node-id`-Attribute wie:

```html
data-node-id="1:2"
```

Dadurch lassen sich Codeelemente wieder konkreten Figma-Nodes zuordnen.

### 7.3 Gelieferte Design-Tokens

| Token / Rolle | Wert |
|---|---|
| Gray/900 | `#212529` |
| Semi-Bold / H5 Heading | Inter Semi Bold, 20 px, Gewicht 600, Line Height 100, Letter Spacing 0 |
| Body Text / Base Color | `#68717A` |
| Body/Base Text | Inter Regular, 16 px, Gewicht 400, Line Height 28, Letter Spacing 0 |
| Default/White | `#FFFFFF` |
| Gray/300 | `#DEE2E6` |
| Primary/Color | `#7749F8` |

### 7.4 Asset-Hinweis

Der MCP speichert Bilder und SVGs im Referenzcode als Konstanten. Die URLs zeigen auf einen temporären Figma-MCP-Asset-Server und sind laut Antwort ungefähr sieben Tage abrufbar. Für dauerhaften Projektcode müssten die exakten Bytes heruntergeladen und im Projekt versioniert oder durch eine dauerhafte Projekt-/CDN-Quelle ersetzt werden.

## 8. Aus dem Designcode extrahierte Assets

```javascript
const imgImage3 = "https://www.figma.com/api/mcp/asset/0db66524-d1ff-4e25-bc20-c975afb20b84";
const imgRectangle313 = "https://www.figma.com/api/mcp/asset/c5ab8d7b-4f46-429b-872d-6a05a46f56e0";
const imgRectangle314 = "https://www.figma.com/api/mcp/asset/03ff7bfe-329a-4029-9d44-767588bc580f";
```

Verwendung im Referenzcode:

- `imgImage3`: großes Bild links, 260 × 260 px, bei `(16, 200)`.
- `imgRectangle313`: Schritt-/Progress-Asset für Schritt 1.
- `imgRectangle314`: Schritt-/Progress-Asset für die Schritte 2 bis 8.

## 9. Extrahierte visuelle Struktur

### 9.1 Wurzel

- React-Komponente: `Desktop`.
- Wurzel-Node: `78:725`.
- Figma-Name: `Desktop`.
- Hintergrund: Weiß.
- Layout im gelieferten Referenzcode: relativ positionierter Container mit mehreren absolut positionierten Bereichen.

### 9.2 Header-Varianten

Der Node enthält mehrere Header-Varianten beziehungsweise wiederholte Header-Layer:

- Header 1: `78:726` bis `78:730`.
- Header 2: `78:741` bis `78:745`.
- Header 3: `196:1324` bis `196:1328`.
- Header 4: `196:1329` bis `196:1333`.

Gemeinsame Eigenschaften:

- Höhe: `110px`.
- Position: oben, links und rechts `0`.
- Innenabstand: horizontal `64px`, vertikal `24px`.
- Ausrichtung: horizontal mit `justify-between`, vertikal zentriert.
- Navigation: `Startseite` und `Kontakt`.
- Abstand zwischen Navigationselementen: `40px`.
- Navigationsschrift: Inter Medium, 16 px, ungefähr `#000000`.
- Großer Titel: Inter Black, 56 px, Tracking `-1.68px`.
- Titelvarianten: `SQL Spell Quest Editor` und `SQL Spell `.

### 9.3 Schrittanzeige

Es gibt acht nummerierte Schritte bei `top: 110px`. Die Schritt-Assets sind jeweils `61.357 × 61.357px` groß.

| Schritt | Container-Node | Asset-Node | Text-Node | X | Textmitte |
|---:|---|---|---|---:|---:|
| 1 | `78:814` | `78:815` | `78:816` | 235 | 265.88 |
| 2 | `78:817` | `78:818` | `78:819` | 344 | 374.88 |
| 3 | `78:820` | `78:821` | `78:822` | 453 | 484.38 |
| 4 | `78:823` | `78:824` | `78:825` | 562 | 593.38 |
| 5 | `78:826` | `78:827` | `78:828` | 671 | 702.38 |
| 6 | `78:829` | `78:830` | `78:831` | 780 | 811.38 |
| 7 | `78:832` | `78:833` | `78:834` | 872 | 903.38 |
| 8 | `78:835` | `78:836` | `78:837` | 981 | 1012.38 |

Eine duplizierte beziehungsweise zweite Node-Gruppe befindet sich bei `196:1334` bis `196:1357` und verwendet dieselben Positionen, Assets und Schritttexte.

- Schritttext: schwarz, Inter Semi Bold, `28.509px`.
- Textausrichtung: zentriert.

### 9.4 Linker Bild- und Erklärungsteil

- Bild-Node: `78:748`, Name `image 3`.
- Dupliziertes Bild-Node: `196:1358`, Name `image 4`.
- Position: links `16px`, oben `200px`.
- Größe: `260 × 260px`.
- Bilddarstellung: `object-cover`.
- Erklärungstext-Node: `78:749`.
- Duplizierter Erklärungstext-Node: `196:1365`.
- Position des Textes: links `26px`, oben `482px`.
- Breite: `311px`.
- Höhe: `52px`.
- Schrift: Inter Semi Bold, `20px`, Farbe `#212529`.
- Text:

> Hier legen wir die Grundsteine unseres Levels fest. Du kannst mir beschreiben was du dir vorstellst und ich zaubere dir ein schönes Hintergrundsbild

### 9.5 Erstes Eingabefeld

- Wrapper: `78:732`, Name `wrap`.
- Position: links `412px`, oben `243px`.
- Layout: vertikale Flexbox.
- Abstand zwischen Überschrift und Karte: `32px`.
- Überschrift: Node `78:733`.
- Überschriftstext: `Verrate mir doch bitte wie das Level heißen soll`.
- Karte: Node `78:734`, Name `cardBody`.
- Karte: weißer Hintergrund, Border `1px solid #DEE2E6`, Radius `12px`, Padding `24px`.
- Platzhalter: Node `I78:734;10:4989`.
- Platzhaltertext: `Schreibe hinein`.
- Platzhalterfarbe: `#68717A`.
- Platzhalterbreite: `459px`.
- Platzhaltertypografie: Inter Regular, `16px`, Line Height `28px`.

Die entsprechende duplizierte Struktur liegt bei `196:1359` bis `196:1361`.

### 9.6 Hintergrundbild-Upload

- Upload-Button-Node: `362:1810`, Name `button`.
- Text-Node: `I362:1810;3725:1143`.
- Position: links `469px`, oben `525px`.
- Hintergrund: `#7749F8`.
- Padding: horizontal `16px`, vertikal `10px`.
- Radius: `6px`.
- Textfarbe: Weiß.
- Schrift: Inter Semi Bold, `16px`, Line Height `18px`.
- Text: `Lade dein gewünschtes Hintergrundsbild hoch`.

### 9.7 Begrüßungs-Eingabefeld

- Wrapper: `78:738`, Name `wrap`.
- Position: links `412px`, oben `680px`.
- Layout: vertikale Flexbox.
- Abstand: `32px`.
- Überschrift: Node `78:739`.
- Überschriftstext: `Wie soll der Nutzer des Levels begrüßt werden? `.
- Karte: Node `78:740`, Name `cardBody`.
- Karte: weiß, Border `1px solid #DEE2E6`, Radius `12px`, Padding `24px`.
- Platzhalter: Node `I78:740;10:4989`.
- Platzhaltertext: `Schreibe hinein`.
- Platzhalterbreite: `459px`.

Die entsprechende duplizierte Struktur liegt bei `196:1369` bis `196:1371`.

### 9.8 Navigation unten

- Weiter-Button: Node `372:1730`.
- Text-Node: `I372:1730;3725:1143`.
- Position: links `763px`, oben `962px`.
- Text: `Weiter`.

- Zurück-Button: Node `372:1731`.
- Text-Node: `I372:1731;3725:1143`.
- Position: links `502px`, oben `968px`.
- Text: `Zurück`.

Beide Buttons verwenden:

- Hintergrund `#7749F8`.
- Padding `16px` horizontal und `10px` vertikal.
- Radius `6px`.
- Inter Semi Bold, `16px`, Line Height `18px`.
- Weiße Schrift.

## 10. Vollständiger gelieferter React/Tailwind-Referenzcode

Der folgende Code ist exakt der vom Figma-MCP gelieferte Referenzcode. Er ist **kein** fertiger Django-Code und darf nicht unverändert in das Zielprojekt übernommen werden.

```jsx
const imgImage3 = "https://www.figma.com/api/mcp/asset/0db66524-d1ff-4e25-bc20-c975afb20b84";
const imgRectangle313 = "https://www.figma.com/api/mcp/asset/c5ab8d7b-4f46-429b-872d-6a05a46f56e0";
const imgRectangle314 = "https://www.figma.com/api/mcp/asset/03ff7bfe-329a-4029-9d44-767588bc580f";

export default function Desktop() {
  return (
    <div className="bg-white relative size-full" data-node-id="78:725" data-name="Desktop">
      <header className="[word-break:break-word] absolute content-stretch flex h-[110px] items-center justify-between leading-[0] left-0 not-italic px-[64px] py-[24px] right-0 text-black top-0" data-node-id="78:726" data-name="Header 1">
        <div className="flex flex-[1_0_0] flex-col font-['Inter:Black'] font-black justify-center min-w-px relative text-[56px] tracking-[-1.68px]" data-node-id="78:727">
          <p className="leading-[1.1]">SQL Spell Quest Editor</p>
        </div>
        <nav className="capitalize content-stretch flex font-['Inter:Medium'] font-medium gap-[40px] items-center relative shrink-0 text-[16px] text-center tracking-[-0.08px] whitespace-nowrap" data-node-id="78:728" data-name="Nav">
          <div className="flex flex-col justify-center relative shrink-0" data-node-id="78:729">
            <p className="leading-[1.45]">Startseite</p>
          </div>
          <div className="flex flex-col justify-center relative shrink-0" data-node-id="78:730">
            <p className="leading-[1.45]">Kontakt</p>
          </div>
        </nav>
      </header>
      <div className="absolute content-stretch flex flex-col gap-[32px] items-start left-[412px] top-[243px]" data-node-id="78:732" data-name="wrap">
        <p className="[word-break:break-word] font-['Inter:Semi_Bold'] font-semibold leading-[normal] not-italic relative shrink-0 text-[#212529] text-[20px] whitespace-nowrap" data-node-id="78:733">
          Verrate mir doch bitte wie das Level heißen soll
        </p>
        <div className="bg-white border border-[#dee2e6] border-solid content-stretch flex items-start p-[24px] relative rounded-[12px] shrink-0" data-node-id="78:734" data-name="cardBody">
          <p className="[word-break:break-word] font-['Inter:Regular'] font-normal leading-[28px] not-italic relative shrink-0 text-[#68717a] text-[16px] w-[459px]" data-node-id="I78:734;10:4989">
            Schreibe hinein
          </p>
        </div>
      </div>
      <div className="absolute content-stretch flex flex-col gap-[32px] items-start left-[412px] top-[680px]" data-node-id="78:738" data-name="wrap">
        <p className="[word-break:break-word] font-['Inter:Semi_Bold'] font-semibold leading-[normal] not-italic relative shrink-0 text-[#212529] text-[20px] whitespace-nowrap" data-node-id="78:739">{`Wie soll der Nutzer des Levels begrüßt werden? `}</p>
        <div className="bg-white border border-[#dee2e6] border-solid content-stretch flex items-start p-[24px] relative rounded-[12px] shrink-0" data-node-id="78:740" data-name="cardBody">
          <p className="[word-break:break-word] font-['Inter:Regular'] font-normal leading-[28px] not-italic relative shrink-0 text-[#68717a] text-[16px] w-[459px]" data-node-id="I78:740;10:4989">
            Schreibe hinein
          </p>
        </div>
      </div>
      <header className="[word-break:break-word] absolute content-stretch flex h-[110px] items-center justify-between leading-[0] left-0 not-italic px-[64px] py-[24px] right-0 text-black top-0" data-node-id="78:741" data-name="Header 2">
        <div className="flex flex-[1_0_0] flex-col font-['Inter:Black'] font-black justify-center min-w-px relative text-[56px] tracking-[-1.68px]" data-node-id="78:742">
          <p className="leading-[1.1]">{`SQL Spell `}</p>
        </div>
        <nav className="capitalize content-stretch flex font-['Inter:Medium'] font-medium gap-[40px] items-center relative shrink-0 text-[16px] text-center tracking-[-0.08px] whitespace-nowrap" data-node-id="78:743" data-name="Nav">
          <div className="flex flex-col justify-center relative shrink-0" data-node-id="78:744">
            <p className="leading-[1.45]">Startseite</p>
          </div>
          <div className="flex flex-col justify-center relative shrink-0" data-node-id="78:745">
            <p className="leading-[1.45]">Kontakt</p>
          </div>
        </nav>
      </header>
      <div className="absolute left-[16px] size-[260px] top-[200px]" data-node-id="78:748" data-name="image 3">
        <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full" src={imgImage3} />
      </div>
      <p className="[word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold h-[52px] leading-[normal] left-[26px] not-italic text-[#212529] text-[20px] top-[482px] w-[311px]" data-node-id="78:749">
        Hier legen wir die Grundsteine unseres Levels fest. Du kannst mir beschreiben was du dir vorstellst und ich zaubere dir ein schönes Hintergrundsbild
      </p>
      <div className="absolute contents left-[235px] top-[110px]" data-node-id="78:814">
        <div className="absolute left-[235px] size-[61.357px] top-[110px]" data-node-id="78:815">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle313} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[265.88px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="78:816">
          1
        </p>
      </div>
      <div className="absolute contents left-[344px] top-[110px]" data-node-id="78:817">
        <div className="absolute left-[344px] size-[61.357px] top-[110px]" data-node-id="78:818">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[374.88px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="78:819">
          2
        </p>
      </div>
      <div className="absolute contents left-[453px] top-[110px]" data-node-id="78:820">
        <div className="absolute left-[453px] size-[61.357px] top-[110px]" data-node-id="78:821">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[484.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="78:822">
          3
        </p>
      </div>
      <div className="absolute contents left-[562px] top-[110px]" data-node-id="78:823">
        <div className="absolute left-[562px] size-[61.357px] top-[110px]" data-node-id="78:824">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[593.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="78:825">
          4
        </p>
      </div>
      <div className="absolute contents left-[671px] top-[110px]" data-node-id="78:826">
        <div className="absolute left-[671px] size-[61.357px] top-[110px]" data-node-id="78:827">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[702.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="78:828">
          5
        </p>
      </div>
      <div className="absolute contents left-[780px] top-[110px]" data-node-id="78:829">
        <div className="absolute left-[780px] size-[61.357px] top-[110px]" data-node-id="78:830">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[811.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="78:831">
          6
        </p>
      </div>
      <div className="absolute contents left-[872px] top-[110px]" data-node-id="78:832">
        <div className="absolute left-[872px] size-[61.357px] top-[110px]" data-node-id="78:833">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[903.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="78:834">
          7
        </p>
      </div>
      <div className="absolute contents left-[981px] top-[110px]" data-node-id="78:835">
        <div className="absolute left-[981px] size-[61.357px] top-[110px]" data-node-id="78:836">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[1012.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="78:837">
          8
        </p>
      </div>
      <header className="[word-break:break-word] absolute content-stretch flex h-[110px] items-center justify-between leading-[0] left-0 not-italic px-[64px] py-[24px] right-0 text-black top-0" data-node-id="196:1324" data-name="Header 3">
        <div className="flex flex-[1_0_0] flex-col font-['Inter:Black'] font-black justify-center min-w-px relative text-[56px] tracking-[-1.68px]" data-node-id="196:1325">
          <p className="leading-[1.1]">SQL Spell Quest Editor</p>
        </div>
        <nav className="capitalize content-stretch flex font-['Inter:Medium'] font-medium gap-[40px] items-center relative shrink-0 text-[16px] text-center tracking-[-0.08px] whitespace-nowrap" data-node-id="196:1326" data-name="Nav">
          <div className="flex flex-col justify-center relative shrink-0" data-node-id="196:1327">
            <p className="leading-[1.45]">Startseite</p>
          </div>
          <div className="flex flex-col justify-center relative shrink-0" data-node-id="196:1328">
            <p className="leading-[1.45]">Kontakt</p>
          </div>
        </nav>
      </header>
      <header className="[word-break:break-word] absolute content-stretch flex h-[110px] items-center justify-between leading-[0] left-0 not-italic px-[64px] py-[24px] right-0 text-black top-0" data-node-id="196:1329" data-name="Header 4">
        <div className="flex flex-[1_0_0] flex-col font-['Inter:Black'] font-black justify-center min-w-px relative text-[56px] tracking-[-1.68px]" data-node-id="196:1330">
          <p className="leading-[1.1]">{`SQL Spell `}</p>
        </div>
        <nav className="capitalize content-stretch flex font-['Inter:Medium'] font-medium gap-[40px] items-center relative shrink-0 text-[16px] text-center tracking-[-0.08px] whitespace-nowrap" data-node-id="196:1331" data-name="Nav">
          <div className="flex flex-col justify-center relative shrink-0" data-node-id="196:1332">
            <p className="leading-[1.45]">Startseite</p>
          </div>
          <div className="flex flex-col justify-center relative shrink-0" data-node-id="196:1333">
            <p className="leading-[1.45]">Kontakt</p>
          </div>
        </nav>
      </header>
      <div className="absolute contents left-[235px] top-[110px]" data-node-id="196:1334">
        <div className="absolute left-[235px] size-[61.357px] top-[110px]" data-node-id="196:1335">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle313} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[265.88px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="196:1336">
          1
        </p>
      </div>
      <div className="absolute contents left-[344px] top-[110px]" data-node-id="196:1337">
        <div className="absolute left-[344px] size-[61.357px] top-[110px]" data-node-id="196:1338">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[374.88px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="196:1339">
          2
        </p>
      </div>
      <div className="absolute contents left-[453px] top-[110px]" data-node-id="196:1340">
        <div className="absolute left-[453px] size-[61.357px] top-[110px]" data-node-id="196:1341">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[484.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="196:1342">
          3
        </p>
      </div>
      <div className="absolute contents left-[562px] top-[110px]" data-node-id="196:1343">
        <div className="absolute left-[562px] size-[61.357px] top-[110px]" data-node-id="196:1344">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[593.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="196:1345">
          4
        </p>
      </div>
      <div className="absolute contents left-[671px] top-[110px]" data-node-id="196:1346">
        <div className="absolute left-[671px] size-[61.357px] top-[110px]" data-node-id="196:1347">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[702.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="196:1348">
          5
        </p>
      </div>
      <div className="absolute contents left-[780px] top-[110px]" data-node-id="196:1349">
        <div className="absolute left-[780px] size-[61.357px] top-[110px]" data-node-id="196:1350">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[811.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="196:1351">
          6
        </p>
      </div>
      <div className="absolute contents left-[872px] top-[110px]" data-node-id="196:1352">
        <div className="absolute left-[872px] size-[61.357px] top-[110px]" data-node-id="196:1353">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[903.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="196:1354">
          7
        </p>
      </div>
      <div className="absolute contents left-[981px] top-[110px]" data-node-id="196:1355">
        <div className="absolute left-[981px] size-[61.357px] top-[110px]" data-node-id="196:1356">
          <img alt="" className="absolute block inset-0 max-w-none size-full" src={imgRectangle314} />
        </div>
        <p className="-translate-x-1/2 [word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold leading-[normal] left-[1012.38px] not-italic text-[28.509px] text-black text-center top-[123.18px] whitespace-nowrap" data-node-id="196:1357">
          8
        </p>
      </div>
      <div className="absolute left-[16px] size-[260px] top-[200px]" data-node-id="196:1358" data-name="image 4">
        <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full" src={imgImage3} />
      </div>
      <div className="absolute content-stretch flex flex-col gap-[32px] items-start left-[412px] top-[243px]" data-node-id="196:1359" data-name="wrap">
        <p className="[word-break:break-word] font-['Inter:Semi_Bold'] font-semibold leading-[normal] not-italic relative shrink-0 text-[#212529] text-[20px] whitespace-nowrap" data-node-id="196:1360">
          Verrate mir doch bitte wie das Level heißen soll
        </p>
        <div className="bg-white border border-[#dee2e6] border-solid content-stretch flex items-start p-[24px] relative rounded-[12px] shrink-0" data-node-id="196:1361" data-name="cardBody">
          <p className="[word-break:break-word] font-['Inter:Regular'] font-normal leading-[28px] not-italic relative shrink-0 text-[#68717a] text-[16px] w-[459px]" data-node-id="I196:1361;10:4989">
            Schreibe hinein
          </p>
        </div>
      </div>
      <p className="[word-break:break-word] absolute font-['Inter:Semi_Bold'] font-semibold h-[52px] leading-[normal] left-[26px] not-italic text-[#212529] text-[20px] top-[482px] w-[311px]" data-node-id="196:1365">
        Hier legen wir die Grundsteine unseres Levels fest. Du kannst mir beschreiben was du dir vorstellst und ich zaubere dir ein schönes Hintergrundsbild
      </p>
      <div className="absolute content-stretch flex flex-col gap-[32px] items-start left-[412px] top-[680px]" data-node-id="196:1369" data-name="wrap">
        <p className="[word-break:break-word] font-['Inter:Semi_Bold'] font-semibold leading-[normal] not-italic relative shrink-0 text-[#212529] text-[20px] whitespace-nowrap" data-node-id="196:1370">{`Wie soll der Nutzer des Levels begrüßt werden? `}</p>
        <div className="bg-white border border-[#dee2e6] border-solid content-stretch flex items-start p-[24px] relative rounded-[12px] shrink-0" data-node-id="196:1371" data-name="cardBody">
          <p className="[word-break:break-word] font-['Inter:Regular'] font-normal leading-[28px] not-italic relative shrink-0 text-[#68717a] text-[16px] w-[459px]" data-node-id="I196:1371;10:4989">
            Schreibe hinein
          </p>
        </div>
      </div>
      <div className="absolute bg-[#7749f8] content-stretch flex items-start left-[469px] px-[16px] py-[10px] rounded-[6px] top-[525px]" data-node-id="362:1810" data-name="button">
        <p className="[word-break:break-word] font-['Inter:Semi_Bold'] font-semibold leading-[18px] not-italic relative shrink-0 text-[16px] text-white whitespace-nowrap" data-node-id="I362:1810;3725:1143">
          Lade dein gewünschtes Hintergrundsbild hoch
        </p>
      </div>
      <div className="absolute bg-[#7749f8] content-stretch flex items-start left-[763px] px-[16px] py-[10px] rounded-[6px] top-[962px]" data-node-id="372:1730" data-name="button">
        <p className="[word-break:break-word] font-['Inter:Semi_Bold'] font-semibold leading-[18px] not-italic relative shrink-0 text-[16px] text-white whitespace-nowrap" data-node-id="I372:1730;3725:1143">
          Weiter
        </p>
      </div>
      <div className="absolute bg-[#7749f8] content-stretch flex items-start left-[502px] px-[16px] py-[10px] rounded-[6px] top-[968px]" data-node-id="372:1731" data-name="button">
        <p className="[word-break:break-word] font-['Inter:Semi_Bold'] font-semibold leading-[18px] not-italic relative shrink-0 text-[16px] text-white whitespace-nowrap" data-node-id="I372:1731;3725:1143">
          Zurück
        </p>
      </div>
    </div>
  );
}
```

## 11. Vorgesehener Ablauf für eine echte Implementierung

Dieser Ablauf wurde durch die Design-to-Code-Anleitung vorgegeben, aber in diesem Turn nicht ausgeführt:

1. Das bestehende Django-Projekt und seine Templates, CSS-Dateien, Komponenten und Tokens weiter analysieren.
2. Prüfen, ob vorhandene Header-, Button-, Formular-, Card- oder Stepper-Komponenten wiederverwendet werden können.
3. Den React/Tailwind-Referenzcode in Django-Template-, HTML- und bestehende CSS-Strukturen übersetzen.
4. Tailwind-Klassen durch die vorhandenen CSS-Regeln beziehungsweise Tokens ersetzen.
5. Die drei exportierten Assets rechtzeitig herunterladen oder an eine dauerhafte Asset-Quelle anbinden, da die MCP-URLs temporär sind.
6. Die wiederholten Figma-Layer als tatsächliche Zielstruktur interpretieren und nicht blind doppelt rendern, sofern sie nur Varianten/duplizierte Designzustände darstellen.
7. Inter-Schrift und die angegebenen Farben, Größen, Abstände, Radien und Positionen übernehmen.
8. Formulareingaben, Upload-Button sowie Zurück-/Weiter-Navigation an die Django-Views und URLs anbinden.
9. Die Seite im Projekt rendern und visuell gegen den gelieferten Screenshot prüfen.
10. Responsive Verhalten ergänzen, da der Figma-Referenzcode überwiegend absolute Desktop-Positionen verwendet.
11. Tests beziehungsweise Django-Checks ausführen und anschließend die geänderten Dateien zusammenfassen.

## 12. Status

- Figma-Design gelesen: ja.
- Request und Antwort dokumentiert: ja.
- Screenshot empfangen: ja.
- Projektcode geändert: nein.
- Assets heruntergeladen: nein.
- Figma-Datei geändert: nein.
- Echte Page-Implementierung gestartet: nein; sie war für diese Dokumentationsaufgabe nicht erforderlich.

