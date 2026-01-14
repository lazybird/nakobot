# AGENT ROLE: Expert en Automatisation Python (Architecture DOE)

## FRAMEWORK : D.O.E (Directive, Orchestration, Execution)

Le système est conçu comme un script éphémère (One-shot) destiné à être lancé par un Cron.

## 1. COUCHE DIRECTIVE (Le "Quoi")

- **Objectif** : Diffuser des leçons de formation sur Telegram.
- **Source** : Google Sheets (Lecture du planning).
- **Mode d'exécution** : Exécution unique (le script se ferme après avoir traité les tâches dues).
- **Sécurité** : AUCUN secret en dur. Utilisation exclusive de variables d'environnement.

## 2. COUCHE ORCHESTRATION (Le "Comment")

- **Fichier** : `main.py`.
- **Logique** :
  1. Initialiser les services (Sheets & Telegram).
  2. Récupérer TOUTES les lignes du Sheets.
  3. Filtrer : `Date d'envoi == Aujourd'hui` ET `Statut == 'À envoyer'`.
  4. Envoyer chaque message identifiée.
  5. Mettre à jour le Sheets pour chaque envoi réussi.
  6. Fermer proprement la connexion.

## 3. COUCHE EXECUTION (Le "Faire")

- `/execution/sheets_service.py` : Gère l'auth via variable d'env `GREETS_SERVICE_ACCOUNT_JSON` et les opérations CRUD.
- `/execution/telegram_service.py` : Envoi simple via `pyTelegramBotAPI`.

## STRUCTURE & DÉPLOIEMENT

- `/directives`, `/execution`, `/orchestration`, `/temp`.
- `Dockerfile` : Basé sur `python:3.11-slim`, exécute `python main.py`.
- `.gitignore` : Doit exclure `.env`, `__pycache__`, et tout fichier de credentials local.

## INSTRUCTIONS POUR ANTIGRAVITY

1. Créer l'arborescence.
2. Générer un `main.py` minimaliste pour un test d'envoi de message "Hello World" sur Telegram.
3. Préparer le `Dockerfile` pour une exécution unique.
