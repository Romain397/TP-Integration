# TP 2 — Tests, couverture et qualité

Projet Python/Django reprenant la stack du TP 1. Django configure les routes dans `orders/urls.py`; `manage.py runserver` démarre le serveur séparément. Les vues sont testées en mémoire avec le client Django.

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

- A1–A2 : utilitaires, validateurs et tests des cas nominaux et limites.
- A3 : exercice d'observation des échecs ; les mutations sont décrites ci-dessous et ne restent pas dans le code livré.
- A4 : `sort_students` et tests suivant les huit cas TDD demandés.
- A5 : `parse_price` avec formats français et erreurs.
- B1 : frais de livraison, codes promo, surge pricing et total de commande.
- B2 : API de simulation, création/recherche de commande et validation promo avec tests HTTP.
- B3–B4/C1 : couverture minimale de 80 %, Ruff et workflow GitHub Actions.

## Exercice A3 — mutations à essayer puis annuler

1. Dans `calculate_average`, remplacer `/` par `*` : les cas de tableaux de plusieurs éléments échouent avec une valeur reçue différente de la valeur attendue.
2. Dans `is_valid_email`, retirer le contrôle de `@` : les adresses `invalid` et `user@` ne sont plus rejetées.
3. Dans `capitalize`, retirer `.lower()` : `WORLD` renvoie `WORLD` au lieu de `World`.
4. Restaurer le code, puis relancer `coverage run manage.py test`.

## Décisions de règles

- Les créneaux sont représentés en heures décimales (`12.5` = 12 h 30). 22 h reste ouvert ; après 22 h le service est fermé.
- Un code promo dont la date d'expiration est aujourd'hui reste valide toute cette journée.
- Pour l'exemple du sujet, 7 km donnent 4,00 € (2 € + 4 km × 0,50 €) ; le calcul illustratif `6 km → 3,50 €` est appliqué tel quel par la règle.
- La liste des commandes et les codes promo sont en mémoire. Remplacer la date du système dans un test est évité en injectant `today` aux tests unitaires ; les routes prennent la date courante.

## Routes

| Méthode | Route | Résultat |
| --- | --- | --- |
| POST | `/orders/simulate` | détail du prix, sans sauvegarde |
| POST | `/orders` | commande enregistrée (201) |
| GET | `/orders/:id` | commande (404 si inconnue) |
| POST | `/promo/validate` | validation et prix remisé |

Exemple JSON de commande : `{"items":[{"name":"Pizza","price":12.5,"quantity":2}],"distance":5,"weight":2,"hour":15,"dayOfWeek":"tuesday"}`.
