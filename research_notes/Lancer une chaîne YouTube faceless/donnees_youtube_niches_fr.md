# Données YouTube France par niche (demande vs concurrence) — NON COLLECTÉES

**Appels mcp__Youtube__* utilisés : 1 tentative sur 45 autorisés, 0 résultat** (date : 2026-10-09).

## Données YouTube (vues, abonnés, dates, durées, Shorts vs long, outliers) pour 8 à 10 niches francophones

### Takeaway
Aucune donnée YouTube n'a pu être collectée : le connecteur HasData YouTube (« Youtube ») exige une nouvelle authentification et l'accès direct à youtube.com est bloqué par le proxy réseau de la session. Ce fichier ne contient donc aucun chiffre ; il ne faut pas s'en servir pour comparer les niches.

### Cited Findings
- Aucune. Le premier appel (`hasdata_youtube_search_getYoutubeSearchResults`, q="outils IA", gl=fr, hl=fr, sortBy=views, date=month, videoType=video) a renvoyé : « MCP server "Youtube" needs you to sign in again (run /mcp to re-authenticate) ». Aucune donnée n'a été retournée.
- Solution de repli testée : récupérer directement une page de recherche youtube.com. Résultat : « CONNECT tunnel failed, response 403 » (hôte bloqué par le proxy de la session).

### Inferences
- Aucune inférence sur la demande ou la concurrence n'est possible à partir de ce travail. Aucun chiffre n'a été remplacé par une estimation ou par des données de mémoire.
- Pour obtenir ces données : reconnecter le connecteur YouTube (HasData) sur https://claude.ai/customize/connectors, puis lancer une **nouvelle** session (les connecteurs ne sont lus qu'au démarrage d'une session) et relancer cette tâche avec le même plan (budget de 45 appels, presque entièrement disponible).

### Gaps
- Vues médianes des meilleurs résultats par niche (IA/outils, histoires d'entreprises, finances personnelles, histoire/documentaire, true crime/faits divers, psychologie, science/espace, géopolitique/économie, histoires racontées) : inconnues.
- Nombre de vidéos outliers venant de petites chaînes (ratio vues/abonnés) par niche : inconnu.
- Comparaison Shorts vs format long, durées types, rythme de publication et ancienneté des chaînes : inconnus.
- Comparaison avec le marché US (gl=us) : non réalisée.
- Idées de vidéos tirées des outliers : aucune, faute de données.
