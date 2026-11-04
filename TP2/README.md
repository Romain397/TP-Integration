# TP 2 — Tests, couverture et qualité

Projet Python/Django reprenant la stack du TP 1. Django configure les routes dans `orders/urls.py`; `manage.py runserver` démarre le serveur séparément. Les vues sont testées en mémoire avec le client Django. Le projet contient **178 tests indépendants**, avec **97,86 % de couverture du code applicatif**, tests exclus du calcul, et un seuil bloquant de 80 %.

## Installation et commandes

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
ruff check .
coverage run manage.py test
coverage report --fail-under=80
python manage.py runserver
```

## Contenu réalisé

- A1 : 18 tests des utilitaires ; A2 : 24 tests des validateurs, avec vérification des messages d'erreur.
- A3 : trois mutations exécutées dans une copie jetable, avec leurs échecs puis leur restauration vérifiés.
- A4 : `sort_students`, les huit cas demandés et deux validations supplémentaires ; rejeu de la progression TDD dans un bac à sable.
- A5–A7 : `parse_price`, `group_by`, `calculate_discount`, avec 34 tests de formats, regroupements, remises et entrées invalides.
- B1 : 64 tests des frais de livraison, promos, créneaux et totaux.
- B2 : 28 tests HTTP de simulation, création/recherche de commande et validation promo.
- B3–B4/C1 : couverture minimale de 80 %, Ruff et workflow GitHub Actions.

Les tests sont séparés dans `orders/test_utils.py`, `orders/test_validators.py`, `orders/test_pricing.py` et `orders/test_api.py`. La CI utilise Python 3.12 et 3.13. Les [captures rouge/vert du dépôt](../TP1/README.md#preuves-du-cycle-rouge--vert) et la [PR de correction](https://github.com/Romain397/TP-Integration/pull/1) conservent les validations distantes.

## Exercices A3 et A4 — preuves reproductibles

```powershell
python scripts/replay-exercises.py
```

Le script copie le projet dans un répertoire temporaire ignoré, applique une mutation à la fois, lance les vrais tests puis restaure le code. Le [rapport A3/A4](docs/exercises.json) contient les résultats réellement exécutés :

1. Division remplacée par multiplication : deux échecs, dont `108 != 12`.
2. `@` obligatoire retiré du motif d'email : deux échecs, les deux adresses valides ne sont plus reconnues par ce motif incorrect.
3. `.lower()` supprimé : un échec, `WORLD != World`.

Le même script rejoue A4 depuis une fonction non implémentée : ajout progressif des huit cas, code minimal quand un nouveau cas échoue, puis vérification de l'implémentation finale avec ses validations supplémentaires. Certains nouveaux cas sont déjà couverts par la généralisation précédente et passent immédiatement ; le rapport le montre. Il s'agit d'un **rejeu explicite**, pas d'une reconstruction supposée de la chronologie des anciens commits.

## Décisions de règles

- Les créneaux sont représentés en heures décimales (`12.5` = 12 h 30). Le déjeuner va de 12 h à 13 h 30 inclus ; 13 h 45 revient au tarif normal. 22 h reste ouvert ; après 22 h le service est fermé.
- Un code promo dont la date d'expiration est aujourd'hui reste valide toute cette journée.
- Pour l'exemple du sujet, 7 km donnent 4,00 € (2 € + 4 km × 0,50 €) ; le calcul illustratif `6 km → 3,50 €` est appliqué tel quel par la règle.
- « Acheter 3, le 4e gratuit » retire 10 € sur quatre articles à 10 €, sans remise si le panier n'en contient que trois. Les groupes gratuits sont calculés sur `buy + free` et les règles s'appliquent dans l'ordre du tableau.
- Les booléens, `NaN` et infinis sont rejetés comme montants/distances/poids ; le corps JSON d'une requête doit être un objet. Une commande invalide n'est jamais enregistrée.
- La liste des commandes et les codes promo sont en mémoire. Les tests unitaires injectent `today` ; les tests HTTP fixent l'horloge de la logique promo au 1er juin 2026. Les tests restent donc stables après expiration des exemples ; en utilisation réelle, les routes prennent la date courante.

## Routes

| Méthode | Route | Résultat |
| --- | --- | --- |
| POST | `/orders/simulate` | détail du prix, sans sauvegarde |
| POST | `/orders` | commande enregistrée (201) |
| GET | `/orders/:id` | commande (404 si inconnue) |
| POST | `/promo/validate` | validation et prix remisé |

Exemple JSON de commande : `{"items":[{"name":"Pizza","price":12.5,"quantity":2}],"distance":5,"weight":2,"hour":15,"dayOfWeek":"tuesday"}`.
