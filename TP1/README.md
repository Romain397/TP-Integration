# API d’annuaire étudiant — Django

[![CI](https://github.com/Romain397/TP-Integration/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Romain397/TP-Integration/actions/workflows/ci.yml)

TP de TDD et intégration continue : API REST Django, tests automatisés, Ruff et GitHub Actions.

## Installation et démarrage

Python 3.12 ou 3.13 est requis.

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate
# macOS/Linux : source .venv/bin/activate
python -m pip install -e ".[dev]"
python manage.py runserver
```

L’API est disponible sur `http://127.0.0.1:8000`.

## Vérifications

```bash
ruff check .
python manage.py test
```

Les étudiants sont conservés dans une liste en mémoire et les tests la réinitialisent avant chaque cas.

## Routes

Les propriétés requises à la création et la modification sont `firstName`, `lastName`, `email`, `grade`, `field`. Les filières admises sont `informatique`, `mathématiques`, `physique` et `chimie`.

| Méthode | Route | Résultat |
| --- | --- | --- |
| GET | `/students` | Liste des étudiants |
| GET | `/students/:id` | Étudiant (400 si ID invalide, 404 si absent) |
| POST | `/students` | Création (201), validation (400), email pris (409) |
| PUT | `/students/:id` | Modification (200), validation (400), absent (404), email pris (409) |
| DELETE | `/students/:id` | Suppression (200), absent (404) |
| GET | `/students/stats` | Effectif, moyenne, nombres par filière, meilleur étudiant |
| GET | `/students/search?q=ahmed` | Recherche insensible à la casse dans nom et prénom |

Exemple de création :

```bash
curl -X POST http://127.0.0.1:8000/students \
  -H "Content-Type: application/json" \
  -d '{"firstName":"Nora","lastName":"Dupont","email":"nora.dupont@example.com","grade":15.5,"field":"physique"}'
```

Le workflow `.github/workflows/ci.yml` s’exécute sur push et pull request vers `main`, avec une matrice Python 3.12/3.13. Les **24 tests** couvrent les routes obligatoires, les validations et les cas limites ; Ruff passe sans erreur.

## Preuves du cycle rouge → vert

La PR [n° 1](https://github.com/Romain397/TP-Integration/pull/1) conserve une exécution rouge puis sa correction, sans introduire de défaut dans `main` :

- [CI rouge — commit f24f65a](https://github.com/Romain397/TP-Integration/actions/runs/41838590960) : les nouveaux tests détectent notamment le crash d'un identifiant `²` et des méthodes HTTP incorrectement acceptées. [Capture réelle](docs/ci-red.png).
- [CI verte — commit dac3edb](https://github.com/Romain397/TP-Integration/actions/runs/41839212859) : les corrections passent les deux versions Python et les autres contrôles du dépôt. [Capture réelle](docs/ci-green.png).

Cette preuve utilise des régressions réelles détectées pendant la revue du sujet, plutôt qu'une panne introduite artificiellement dans l'API livrée. Les captures montrent les pages GitHub Actions et les liens permettent de vérifier leurs résultats.
