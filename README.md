# TDD et intégration continue

[![CI](https://github.com/Romain397/TP-Integration/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Romain397/TP-Integration/actions/workflows/ci.yml)
[![CodeQL](https://github.com/Romain397/TP-Integration/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/Romain397/TP-Integration/actions/workflows/codeql.yml)

Ce dépôt contient les trois travaux pratiques du cours :

- [TP1](TP1/) — API d’annuaire étudiant avec Django.
- [TP2](TP2/) — tests, validations, moteur de tarification, API, couverture et qualité.
- [TP3](TP3/) — API Node.js sécurisée, audits, CodeQL, Docker, architecture AWS et coûts.

Le workflow GitHub Actions à la racine exécute le lint et les tests des projets Python, vérifie le seuil de couverture de 80 % du TP2 et les tests, dépendances et image Docker du TP3. Un workflow CodeQL analyse le code JavaScript. Le déploiement AWS par OIDC est préparé et désactivé par défaut.

| Projet | Validation |
| --- | --- |
| TP1 | 24 tests, Ruff, matrice Python 3.12/3.13, captures CI rouge/vert |
| TP2 | 178 tests, 97,86 % de couverture applicative, seuil de 80 %, Ruff et rejeu A3/A4 |
| TP3 | 36 tests, audit de production sans vulnérabilité, CodeQL, image non-root sans CVE HIGH/CRITICAL détectée |

Les corrections et les preuves sont conservées dans la [PR n° 1](https://github.com/Romain397/TP-Integration/pull/1). Les trois projets sont réunis sur `main`, protégée par une PR obligatoire et les contrôles CI et sécurité.
