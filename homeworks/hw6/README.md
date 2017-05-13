Poznámky:
- Testoval jsem oba typy doporučování:
  - Content-based funguje, doporučené filmy se podobají žánrem tomu, co všechno daný uživatel hodnotil.
  - Collaborative filtering ok:
    - Zohlednění jednoho usera -> top doporučené filmy jsou ty, které on ohodnotil jako top
    - Zohlednění dvou userů -> top filmy jsou buď ty, které user1 hodnotil jako top, ale které user2 nehodnotil nijak nebo top (takže jsou pořád na top). Pokud film user1 hodnotil jako top, ale user2 jako míň, pak už nahoře nebudou, podle očekávání.Navíc všechny top filmy, které jsou hodnocené jen userem1 jsou nad top filmy, které hodnotil jem user2 (protože user1 je podobnější hledanému uživateli, tak mají jeho hodnocení větší váhu).