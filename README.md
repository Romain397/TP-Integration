# API REST — Annuaire étudiant

TP de TDD et intégration continue : API Flask avec stockage en mémoire, tests pytest, linter Ruff et pipeline GitHub Actions.

## Prérequis et démarrage

Python 3.11 ou 3.12 est requis.

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate
# macOS/Linux : source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m src
```

Le serveur écoute sur `http://127.0.0.1:5000`.

## Qualité

```bash
ruff check .
pytest
```

Les tests réinitialisent les données en mémoire avant chaque cas. Le jeu initial contient cinq étudiants.

## Endpoints

Tous les endpoints renvoient du JSON. Les champs obligatoires à la création et à la modification sont `firstName`, `lastName`, `email`, `grade` et `field`. Les filières autorisées sont `informatique`, `mathématiques`, `physique` et `chimie`.

| Méthode | Route | Résultat |
| --- | --- | --- |
| GET | `/students` | Liste des étudiants |
| GET | `/students/:id` | Étudiant, 400 si l’identifiant est invalide, 404 s'il est absent |
| POST | `/students` | Création (201), validation (400), email déjà pris (409) |
| PUT | `/students/:id` | Modification (200), validation (400), absent (404), email déjà pris (409) |
| DELETE | `/students/:id` | Suppression (200), absent (404) |
| GET | `/students/stats` | Effectif, moyenne, répartition par filière, meilleur étudiant |
| GET | `/students/search?q=ahmed` | Recherche insensible à la casse dans prénom et nom |

Exemple de création :

```bash
curl -X POST http://127.0.0.1:5000/students \
  -H "Content-Type: application/json" \
  -d '{"firstName":"Nora","lastName":"Dupont","email":"nora.dupont@example.com","grade":15.5,"field":"physique"}'
```

Le workflow `.github/workflows/ci.yml` s'exécute sur les pushes et pull requests vers `main`, avec une matrice Python 3.11/3.12 : installation, lint, puis tests.

## Rendu GitHub

Pour terminer le rendu demandé par le cours, créez un dépôt GitHub public, poussez cette branche sur `main`, puis joignez les captures d'un passage rouge et d'un passage vert obtenues pendant la démonstration Red → Green. Le workflow CI est prêt à s'exécuter dès que le dépôt est publié.
