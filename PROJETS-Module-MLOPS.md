# MLOps&DataOps_PFM

Appel à Projets
Module MLOps & DataOps

> Pr. Mohammed AIT DAOUD

## Contexte

Dans le cadre du module MLOps & DataOps, les étudiants sont invités à réaliser un projet de groupe visant à concevoir, développer et industrialiser une solutionData & Intelligence Artificielle en appliquant les concepts, méthodes et outils étudiés durant le cours.

L'objectif n'est pas uniquement de développer un modèle de Machine Learning, mais de mettre en œuvre l'ensemble du cycle de vie d'un projet Data/IA selon les principes du DataOps, duMLOps, de l'Agilité et du Lean thinking.

Les projets devront démontrer la capacité des étudiants à transformer des données brutes en un produit data ou IA exploitable, fiable, maintenable et industrialisable.

## Objectifs pédagogiques
À travers ce projet, les étudiants devront appliquer les notions suivantes :

### Fondements MLOps & DataOps
-  Data Strategy
-  Data Product
-  Data Consumer
-  Gouvernance des données
-  Reproductibilité
-  Versionnement
-  Monitoring
-  Observabilité
-  LLMOps (si applicable)

### Pipelines agiles et orchestration

-  Git et GitHub
-  Gestion Agile de projet
-  User Stories
-  Sprint Planning
-  Sprint Review
-  Sprint Retrospective
-  dlt
-  DuckDB
-  dbt
-  Dagster
-  CI/CD

### Qualité des données

-  Complétude
-  Validité
-  Cohérence
-  Intégrité
-  Fraîcheur
-  Tests automatisés
-  Data Contracts
-  Data Lineage
-  Métadonnées

### Machine Learning

Chaque projet devra intégrer au minimum un composant de Machine Learning
permettant :

-  Classification
-  Régression
-  Clustering
-  Détection d'anomalies
-  Recommandation
-  Prévision

selon la nature du sujet choisi.

### Organisation des équipes
Les projets seront réalisés en groupes de :

-  7 à 10 étudiants

Chaque équipe devra adopter une organisation Agile et répartir les rôles suivants :

-  Product Owner
-  ScrumMaster
-  Data Engineer
-  ML Engineer
-  Data Analyst

Un même étudiant peut cumuler plusieurs rôles selon la taille du groupe.

### Architecture minimale attendue
Chaque projet devra comporter l'architecture suivante :

DuckDB dbt Tests Qualité Dagster
Sources de dlt (Ingestion

(Stockage (Transformat (Data (Orchestratio
données automatisée)

local) ions) Contracts) n)

Monitoring CI/CD Tracking & Machine
Conteneurisa Service ML

& (GitHub Registry Learning
tion (Docker) (FastAPI)

Observabilité Actions) (MLflow) (Scikit-Learn)

## Livrables obligatoires
### Livrable 1 : Vision du projet

Document présentant :

-  Problématique
-  Objectifs
-  Utilisateurs cibles
-  Valeur métier
-  Data Strategy

### Livrable 2 : Gestion Agile

-  Product Backlog
-  User Stories
-  Planning des sprints
-  Sprint Reviews
-  Sprint Retrospectives

### Livrable 3 : Dépôt GitHub

Le dépôt devra contenir :

-  Code source
-  Historique Git
-  README
-  Documentation

### Livrable 4 : Pipeline DataOps

Mise en œuvre complète :

-  dlt
-  DuckDB
-  dbt
-  Dagster

### Livrable 5 : Qualité des données

Mise en place de :

-  Tests de qualité
-  Data Contract
-  Documentation des données

### Livrable 6 : Composant Machine Learning

Le projet devra intégrer :

-  Préparation des données
-  Entraînement du modèle
-  Évaluation
-  Versionnement
-  Monitoring des performances

### Livrable 7 : Présentation finale

Rapport final

Présentation orale :

-  Durée : 15 minutes
-  Démonstration : 10 minutes
-  Questions : 5 minutes

### Livrable 1— Vision du projet

-  Problématique  
-  Objectifs  
-  Utilisateurs Cibles 
-  Valeur métier  
-  Data Strategy

### Livrable 2— Gestion Agile

Minimum : 

-  Product Backlog  
-  User Stories  
-  Sprint Planning  
-  Sprint Review  
-  Sprint Retrospective  

Au moins : 3 sprints

### Livrable 3— Pipeline DataOps

Utilisation obligatoire de : 

-  dlt  
-  DuckDB  
-  dbt  
-  Dagster  

### Livrable 4— Qualité des données

Mise en place de :

-  Tests de qualité
-  Data Contract
-  Documentation des données

### Livrable 5—Machine Learning

Le projet doit contenir : 

-  Préparation des données  
-  Entraînement  
-  Évaluation  
-  Sauvegarde du modèle  

### Livrable 6—MLflow

Obligatoire : 

-  Experiment Tracking  
-  Paramètres  
-  Métriques  
-  Artefacts  
-  Registry  

### Livrable 7— Déploiement

Obligatoire : 

-  FastAPI  
-  Docker  

Exposition minimale : 

POST /predict
GET /health

### Livrable 8— CI/CD

GitHub Actions :

-  Tests automatiques  
-  Build Docker  
-  Vérification du code  

### Livrable 9—Monitoring

Suivi de : 

-  disponibilité du service  
-  temps de réponse  
-  métriques ML  
-  dérive simple 

### Livrable 10— Documentation

GitHub : 

-  README  
-  Architecture  
-  Guide d'installation  
-  Guide d'utilisation 

### Livrable finale : Présentation

Présentation orale :

-  Durée : 15 minutes
-  Démonstration : 10 minutes
-  Questions : 5 minutes

Exemples de sujets proposés
Les équipes peuvent également proposer un sujet original sous réserve de validation par
moi-même.

| N° | Projet | Domaine | Objectif ML |
| ---: | --- | --- | --- |
| 1 | Learning Analytics pour LMS (Moodle) | Éducation | Prédiction des étudiants à risque |
| 2 | Plateforme intelligente de réussite | Éducation | Prédiction de réussite/échec universitaire |
| 3 | Détection de fraude bancaire | Finance | Classification des transactions frauduleuses |
| 4 | Scoring de crédit intelligent | Finance | Évaluation du risque client |
| 5 | Smart Agriculture Analytics | Agriculture | Prédiction des rendements agricoles |
| 6 | Monitoring énergétique intelligent | Énergie | Prévision de consommation |
| 7 | Maintenance prédictive industrielle | Industrie 4.0 | Prédiction des pannes |
| 8 | Analyse prédictive du trafic routier | Smart City | Prévision de congestion |
| 9 | Prédiction des retards aériens | Transport | Classification des retards |
| 10 | Observatoire intelligent des prix | Immobilier | Estimation des prix immobiliers |
| 11 | Détection d'anomalies IoT | IoT | Détection d'anomalies |
| 12 | Système de recommandation de films | Divertissement | Recommandation personnalisée |
| 13 | Système de recommandation de livres | Culture | Recommandation personnalisée |
| 14 | Analyse des avis clients | Marketing | Analyse de sentiments |
| 15 | Détection de Fake News | Médias | Classification NLP |
| 16 | Assistant conversationnel universitaire | LLMOps | Chatbot spécialisé étudiants |
| 17 | Assistant juridique intelligent | LLMOps | Recherche et réponse documentaire |
| 18 | Assistant médical documentaire | Santé | Question-réponse assistée par IA |
| 19 | Prévision de la qualité de l'air | Environnement | Séries temporelles |
| 20 | Plateforme de cybersécurité intelligente | Cybersécurité | Détection d'intrusions |

## Contraintes obligatoires pour TOUS les projets
Chaque groupe devra obligatoirement mettre en œuvre : 

### Partie Agile 

-  Product Backlog  
-  User Stories  
-  3 Sprints minimum  
-  Sprint Review  
-  Sprint Retrospective  

### Partie DataOps 

-  dlt  
-  DuckDB  
-  dbt  
-  Dagster  

### Partie Qualité 

-  Tests qualité  
-  Data Contract  
-  Data Lineage  

### Partie MLOps 

-  Modèle ML  
-  Évaluation  
-  Versionnement  
-  Monitoring  

### Partie Collaboration 

-  Git  
-  GitHub  
-  Pull Requests  

## Objectif final
L'objectif de ce projet est de permettre aux étudiants de réaliser un projet complet de type industriel intégrant les dimensions DataOps, MLOps, Agile et Machine Learning, depuis la définition du besoin jusqu'au déploiement d'une solution exploitable et maintenable.
