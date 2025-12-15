# Solution Hashcode 2017 - Streaming Videos

Ce projet propose une solution optimale pour le problème de qualification du **Google Hash Code 2017** : _Streaming Videos_.
L'implémentation est réalisée en Python et utilise le solveur **Gurobi** pour maximiser les économies de latence.

## Description du problème

L'objectif est d'optimiser la distribution de vidéos dans des serveurs de cache pour minimiser le temps d'attente total des utilisateurs.

## Prérequis

Avant de lancer le projet, assurez-vous d'avoir :

- **Python 3.x** installé.
- Une licence **Gurobi** valide (une licence académique ou d'évaluation est nécessaire pour les instances de grande taille).
- Les bibliothèques Python nécessaires (notamment `gurobipy`).

## Installation

1.  **Cloner le projet** ou extraire l'archive.
2.  **Créer un environnement virtuel** (recommandé) :
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```
    _(Si `requirements.txt` n'existe pas, installez manuellement : `pip install gurobipy`)_

## Structure du projet

Projet_Opti/
├── data_projet/ # Dossier contenant les jeux de données (.in)
├── videos.py # Script principal de résolution
└── README.md # Documentation du projet

````

## Utilisation

Pour lancer la résolution sur un fichier d'entrée spécifique (par exemple `trending_4000_10k.in`) :

```bash
python videos.py data_projet/videos/datasets/trending_4000_10k.in
````

### Fonctionnement du script

Le script `videos.py` effectue les étapes suivantes :

1.  **Lecture** : Analyse le fichier `.in` fourni en argument.
2.  **Modélisation** : Construit un modèle d'optimisation linéaire mixte (MIP) avec Gurobi.
3.  **Résolution** : Lance l'optimiseur (avec une tolérance d'arrêt _MIP Gap_ de 0.5%).
4.  **Sortie** :
    - Sauvegarde le modèle (`videos.mps`) dans le répertoire courant.
    - Écrit la solution finale (`videos.out`) dans le répertoire courant.

## Auteur

Projet réalisé dans le cadre d'un cours d'optimisation.
