# Élise

Prototype d'une IA de conversation bienveillante pour les adultes qui se sentent
seuls — d'abord les quadragénaires séparés ou divorcés.

**Prototype de test uniquement.** Pendant le développement, Élise répond avec
l'offre gratuite de l'API Gemini, dont Google peut réutiliser les données. On
n'y tape donc que des conversations fictives, jamais de vraies confidences.

## Règle d'or : zéro dépense

Tout tourne sur des offres gratuites, sans carte bancaire :

| Service  | Rôle                              | Offre         |
| -------- | --------------------------------- | ------------- |
| Vercel   | héberge le site                   | Hobby         |
| Supabase | comptes et base de données        | Free          |
| Gemini   | le modèle qui fait parler Élise   | gratuite (AI Studio) |

Aucune étape ne demande d'activer la facturation. Si un écran le propose, on
refuse.

## Ce qu'il y a dans ce dossier

- `elise-persona.md` — qui est Élise, comment elle parle, ses limites, et son
  premier message. C'est le fichier à retoucher pour changer sa personnalité,
  sans toucher au code. Le titre `## Premier message` doit rester : l'application
  y cherche le message d'accueil des nouveaux venus.
- `lib/llm.ts` — le seul fichier qui parle au modèle. Tout le reste passe par
  lui.
- `lib/persona.ts` — lit la persona et en extrait le premier message.
- `app/` — les pages du site.
- `scripts/essai-llm.ts` — un essai du modèle en ligne de commande, sans site ni
  base : `npm run essai:llm`.
- `.env.example` — la liste des réglages (clés, choix du modèle).

## Passer de Gemini à Claude

Le jour venu, sur Vercel (**Settings → Environment Variables**) :

1. ajouter `ANTHROPIC_API_KEY` (clé créée sur console.anthropic.com — payant) ;
2. changer `LLM_PROVIDER` de `gemini` à `claude` ;
3. redéployer.

Le modèle par défaut est Claude Haiku 4.5. `CLAUDE_MODEL` permet d'en choisir
un autre, `GEMINI_MODEL` de même côté Gemini (par défaut `gemini-flash-latest`,
qui suit le Flash le plus récent).

## Où en est-on

- [x] **1. Fondations** — le projet, la persona, le branchement au modèle.
- [ ] **2. Base de données** — tables `messages`, `user_facts`, `summaries`,
      sécurité au niveau des lignes.
- [ ] **3. Connexion et conversation** — inscription par e-mail, page de chat,
      premier message d'Élise.
- [ ] **4. Mémoire** — fiche de l'utilisateur, résumés, bouton « Effacer toutes
      mes données ».
- [ ] **5. Mise en ligne** — déploiement Vercel et essais sur téléphone.

## Développer sur sa machine (facultatif)

```bash
cd elise
cp .env.example .env.local   # puis remplir les clés
npm install
npm run dev                  # http://localhost:3000
```
