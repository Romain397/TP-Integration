# TDD et intégration continue

Ce dépôt contient les trois travaux pratiques du cours :

- [TP1](TP1/) — API d’annuaire étudiant avec Django.
- [TP2](TP2/) — tests, validations, moteur de tarification, API, couverture et qualité.
- [TP3](TP3/) — API Node.js sécurisée, audits, CodeQL, Docker, architecture AWS et coûts.

Le workflow GitHub Actions à la racine exécute le lint et les tests des projets Python, vérifie le seuil de couverture de 80 % du TP2 et les tests, dépendances et image Docker du TP3. Un workflow CodeQL analyse le code JavaScript. Le déploiement AWS par OIDC est préparé et désactivé par défaut.
