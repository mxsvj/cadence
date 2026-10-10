# Modèle de montage YouTube (chaîne anglaise, sans visage)

Démo : « The real price of a €100,000 house in France ». La voix est une voix de synthèse de démonstration ; dans les vraies vidéos, elle est remplacée par la voix off ElevenLabs.

## Style retenu

- **Sous-titres : karaoké.** Tout ce que dit la voix est sous-titré mot pour mot, dans un bandeau foncé. Chaque mot passe au jaune quand il est prononcé. Les lignes sont coupées aux virgules et aux fins de phrase, et calées sur les pauses de la voix.
- **Mouvement** : zoom lent permanent, transitions entre les plans (glissements, montée, ouverture en cercle, fondu au noir), apparitions animées avec rebond, surlignage synchronisé avec la voix, zooms « punch » sur les mots clés.
- **Habillage** : compteur « REAL COST » en haut à gauche, barre des chapitres en haut au centre, rappel « Abonne-toi » animé vers le premier tiers.
- **Son** : musique lo-fi chill qui baisse automatiquement sous la voix. Bruitages (whoosh, pop, impact, tic-tac, clochette, clic) **baissés de 6 dB**. Volume final à −14 LUFS, le niveau standard de YouTube.
- **Livrables** : vidéo 16:9 en 1080p, Short 9:16 (fond flouté, titre en haut), écran de fin de 20 s prêt pour YouTube Studio.

## Fabrication

1. `python3 build_scenes.py` : dessine les plans, anime les scènes, génère la voix provisoire, les bruitages et les transitions. Les fichiers intermédiaires vont dans `assets2/`.
2. `python3 build_final.py` : ajoute les zooms punch, le compteur, la barre des chapitres, le rappel d'abonnement, la musique lo-fi et les sous-titres. Les vidéos finales vont dans `out5/`.
3. `python3 build_thumbnails.py` : génère 3 miniatures dans le même style (prix barré, compteur, titre), à comparer avec l'outil « Test & compare » de YouTube Studio.

Les scripts utilisent ffmpeg, Pillow, numpy et la police Inter. RHVoice n'est utilisé que pour la voix provisoire.
