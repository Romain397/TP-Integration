# API d’annuaire étudiant — Django

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

Le workflow `.github/workflows/ci.yml` s’exécute sur push et pull request vers `main`, avec une matrice Python 3.12/3.13.
