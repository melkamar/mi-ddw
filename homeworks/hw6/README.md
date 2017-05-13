Poznámky:
- Testoval jsem oba typy doporučování:
  - Content-based funguje, doporučené filmy se podobají žánrem tomu, co všechno daný uživatel hodnotil.
  - Collaborative filtering ok:
    - Zohlednění jednoho usera -> top doporučené filmy jsou ty, které on ohodnotil jako top
    - Zohlednění dvou userů -> top filmy jsou buď ty, které user1 hodnotil jako top, ale které user2 nehodnotil nijak nebo top (takže jsou pořád na top). Pokud film user1 hodnotil jako top, ale user2 jako míň, pak už nahoře nebudou, podle očekávání.Navíc všechny top filmy, které jsou hodnocené jen userem1 jsou nad top filmy, které hodnotil jem user2 (protože user1 je podobnější hledanému uživateli, tak mají jeho hodnocení větší váhu). Stejně tak to sedí i na ty nejhorší filmy.


- Hybridní testování (0.7, 0.3) -> nejlepší je pro uživatele Wargames. To má celkově skóre 3.621, což je lepší průměr. Žánry filmu jsou ale Drama, Sci-Fi a Thriller, což jsou nejvíce hodnocené žánry uživatele:
  - Drama: 1.0
  - Thriller: 1.0
  - Adventure: 0.75
  - Sci-Fi: 0.75
  - Action: 0.5
  - Comedy: 0.5
  - Horror: 0.5
  - Animation: 0.25
  - Children: 0.25
  - Crime: 0.25
  - Fantasy: 0.25
  - Musical: 0.25
  - Romance: 0.25
  - Western: 0.25

Tento film byl navíc hodnocen pěti hvězdami uživatelem #78, což je druhý nejpodobnější uživatel. Jiní z uvažovaných podobných uživatelů film neohodnotili. Proto bude mít vysoké skóre a bude doporučen.