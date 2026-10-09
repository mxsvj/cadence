# Les tests

```bash
bash test/tout.sh
```

Chromium est déjà là (`/opt/pw-browsers`), seul `playwright-core` s'installe.

| suite | ce qu'elle garde |
|---|---|
| `syntaxe.js` | le script de la page se parse |
| `fumee.js` | on visite tout et on clique sur toutes les actions sans une erreur |
| `structure.js` | trois onglets, l'entraînement en accueil, et plus la moindre trace du jeu social |
| `seance.js` | composer une séance, la dérouler série par série, la retrouver au carnet |
| `images.js` | une image par exercice, jamais la même deux fois, jamais hors cadre |
| `corps.js` | la rampe de récupération reste une rampe valide, et les muscles tiennent dans la silhouette |
| `journal.js` | poids, besoins caloriques, repas, humeur |
| `fab.js` | le bouton + s'efface en descendant et revient en remontant |

Une première version de ces suites vivait dans un dossier temporaire de session.
Un redémarrage de machine l'a effacée — d'où celle-ci, dans le dépôt.
