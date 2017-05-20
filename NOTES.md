# Poznámky - 2016/2017

*V tomto dokumentu jsem se pokusil sumarizovat informace, ručně vytažené ze slajdů přednášek. Píšu je formou "jak mi to padne na jazyk", takže to může být nespisovně, napůl anglicky, všelijak. Pull requesty vítány.*

## Crawling
- Automatický sběr obsahu na webu, rekurzivně se prochází linky na stránkách a zanořuje se hlouběji a hlouběji.
- Existují specializované nástroje - bots, spiders. Ty většinou umí aplikovat policies - nenavštěvovat tutéž stránku víckrát, ignorovat linky na obrázky, css, atd.
- Problémy:
    - Web je moc velký, musí se vybrat co stahovat.
    - Etika - nedosovat servery, používat User-Agenta, `robots.txt`.
- Terminologie:
    - Seed pages - seznam počátečních URL, ze kterých se pak jede dál
    - Frontier - seznam URL, které čekají na prozkoumání, tj. jakási fronta
    - Fetcher - řeší stahování stránky
    - Link Extractor - řeší parsování stránky a přidávání nových URL do Frontieru (to jsme dělali v úkolu pomocí např. CSS selektorů)
    - URL Filter, Duplicate elmiminator, URL prioritizer

#### Strategie crawlování
- BFS
    - klasický grafový BFS, čim dřív přidám URL do fronty, tím dřív ho pak resolvnu
- Backlink
    - před rozhodnutím, kterou stránku procesovat, si je seřadím podle toho, kolik URL v seznamu na ní ukazuje (tj. kolikrát je v seznamu)
    - Jako první budu řešit stránky, na který je hodně odkazů, takže asi budou důležitý.

Pro kontrolu, kdy se stránka naposled změnila a jestli má cenu jí přecrawlovávat můžu použít `HTTP HEAD`

Je třeba řešit URL normalizaci - transformace URL do její kanonické formy. Něco jako v Linuxu převádění relativní cesty, symlinky atd. na absolutní cestu. Tady se řeší např.:
- Velikost písmen
- Percent-encoding (%20 místo mezery)
- Resolving `.` a `..`

#### robots.txt
- Říká co můžu a co nemůžu indexovat (ale nikdo to neenforcuje - je to o etice)
- Příklad - zakázat GoogleBotu přístup do secret, ale všichni ostatní můžou:
```
User-agent: GoogleBot
Disallow: /secret/
Crawl-delay: 5

User-agent: *
Disallow:
```
- Tohle jde určovat i přímo v HTML stránky (*head.meta*).
- V headeru HTTP lze posílat direktivy botům: `noindex`, `noarchive`, `all`, `nofollow` ...

- Sitemap - standardizovaný XML formát, jak pomoct robotům v indexování:
```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema‐instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/
    <url>
        <loc>http://fit.cvut.cz/</loc>
        <lastmod>2014‐02‐27T15:26:35+00:00</lastmod>
        <changefreq>hourly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>
```

#### Specific content
- Deep Web - schovaný za formama, přihlašováním, paywally
    - Kontextuální (podle fyzické lokace)
    - Dynamické stránky (response na search query)
    - Non-HTML (videa, audio)
    - Soukromý web

- Obecně se dá těžko projít, dají se dělat věci jako hledání formů v HTML, zkoušet je vyplňovat, upravovat URL query ručně.
- Některý CAPTCHA jdou obejít, některý ne.
- AJAX stránky - jdou crawlovat když jsou dobře napsaný (např.  query `../#!inbox` bot předělá na `../_escaped_fragment_=inbox`, a tohle Google pochopí a naservíruje content, ale obecně problém.
- Spider pasti, dynamický nekonečný generování linků.

- Obsah stránky lze dolovat klasicky nástrojema pro zpracování textu, machine learning, regexpama (odhalí email adresy, telefonní čísla atp.), nějakým učicím automatem, který si postaví z HTML strom a hledá vhodný patterny.
- HTML může být taky anotovaný, aby boti věděli co to je. Např.
```html
<p vocab="http://schema.org/" typeof="Person">
    <span property="name">Christopher Froome</span> was sponsored by
    <span property="sponsor" typeof="http://schema.org/Organization">
    <a property="url" href="http://www.skysports.com/">Sky</a></span> in the Tour de France.
</p>
```
- Je třeba HTML fixnout, ne vždy bude validní.

## Web Data Mining - Indexing & Document retrieval
#### Information retrieval
- Nalezení dokumentů, který uživatelé chtěji, tedy:
    - Na základě sady existujících dokumentů a dotazu
    - Vytvoř ohodnocenou sadu relevantních dokumentů
    - Chci to rychle, napříč milionama nestrukturovaných dokumentů, spolehlivě, škálovatelně.

#### Modely
- jak jsou dokumenty reprezentované
- Boolean model
    - V dokumentech se uvažuje jenom to, jestli se v nich daný term vyskytuje nebo ne (0/1)
    - Queries se udávají booleovskými operátory a termy stylem `term1 AND (term2 OR term3)`.
    - Pro retrieval se řeší *jenom* přesná shoda - dokument buď relevantní je, nebo není.
- Vector Space model
    - Dobře známý a obecně používaný model
    - Používá **TF-IDF** váhové schéma:
        - TF - term frequency - počet výskytů termu v dokumentů (normalizováno celkovým počtem termů v dokumentu)
        - IDF - inverse document frequency - udává, jak je slovo běžné napříč všemi dokumenty: ![tfidf formula](resources/tfidf.png)
        - *TF-IDF = TF × IDF*

    - Příklad:

        > Slovo se vyskytuje 5x v dokumentu se 100 unikátními slovy -> TF = 5/100

        > Máme 10 000 dokumentů a slovo je (alespoň jednou) ve 100 z nich -> IDF = log(10000/100) = 2

        > TF-IDF = 5/100 * 2 = 1/10

#### Vector space ranking
- který dokument zvolit, který je nejpodobnější?

- Query je množina slov, na jejím základě nějak vyberu dokumenty, které obsahují alespoň jedno ze slov
- Query reprezentuju jako vektor (slova -> čísla) (_"hello world hello" -> (1, 0.5)_, první složka je pro _hello_, druhá pro _world_, normalizovaně)
- Každý kandidátní dokument (docX) reprezentuju jako vektor, kde složky vektoru jsou TF-IDF slov z **query**: (tfidf(hello, docX), tfidf(world, docX))
- Spočtu vzdálenost vektoru Query a vektoru *každého* z dokumentů, seřadím od nejbližšího, to jsou moje výsledky.

- Vzdálenosti:
    - Eukleidovská - klasicky odmocnina ze součtu druhých mocnin, není dobrá, protože když budu mít v query (term1, term2), tak potom s každou další dvojicí termů term1 a term2 v dokumentu bude vzdálenost růst, i když by logicky měla bejt cca stejná.
    - Cosinová - lepší, místo vzdálenosti vektorů se počítá úhel mezi nimi, takže předchozí problém nenastává:

        ![](resources/cosine-distance.PNG)

        Ve jmenovateli je jednoduše násobení vektorů po složkách.
        Pokud jsou vektory totožné, mají úhel 0 a cos(0) = 1.

#### Evaluation measures
- jak hodnotit kvalitu systému?
- Precision - kolik z vrácených dokumentů je skutečně relevantních? - P(relevant | retrieved)
- Recall - kolik z celkem relevantních dokumentů bylo vráceno? - P(retrieved | relevant)
- F-measure - tradeoff mezi precision/recall:

    ![](resources/fmeasure.PNG)

#### Indexing
- sémantika dokumentů a queries jde zachytit množinou index termů - klíčových slov
- **Document index** - klíčová slova, popisující dokument
- indexing - proces vytváření indexu pro každý dokument
- index dokumentů pracuje s *vocabulary* - množinou klíčových slov
    - manuální indexování
        - omezená vocabulary, vytvořena před indexováním
        - kvalitní keywordy, člověk rozumí obsahu, abstrahuje
        - člověk si nevzpomene na celou knihu při indexaci, drahé, pomalé, nekonzistentní
    - automatické indexování
        - nekontrolovaná vocabulary, tvoří se dynamicky při indexaci
        - chcem imitovat lidi, používáme omezený počet termů

- **Inverted index**
    - mapování "keyword" -> "doc1, doc2"
    - tohle je většinou to, co se myslí indexem
    - buduje se předem, na ve chvíli kdy se řeší query
    - používají se standardní struktury pro mapy - hashtables, B-trees
        - hashtable rychlejší lookup, ale při rozumně omezeným počtu termů
        - B-tree delší hledání, ale umí prefix search a najít podobný slova

## Web Data Mining - Text Mining

## Todo - zařadit
Kroky text miningu:

1. Tokenizace (nalezení kapitol, vět, slov)
2. POS tagging (určení slovních druhů)
3. Určení anafor (referencí typu *Mr. Smith* did (...) when *he* saw...
4. Lematizace (převod slova do základního tvaru), stemming (získání kořene slova)
5. Nalezení entit v textu (Named Entity Recognition) - místa, lidi, instituce
6. Gazetteery (???)
7. Získání relací mezi entitami