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
