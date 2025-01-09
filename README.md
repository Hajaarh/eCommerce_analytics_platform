# Documentation du Projet CRM eCommerce

#### Projet CRM eCommerce : Analyse et Visualisation de données avec MongoDB, FastAPI et Streamlit.

Le projet CRM eCommerce repose sur l’utilisation de technologies modernes telles que MongoDB, FastAPI, et Streamlit pour :

- Importer et traiter des données clients, produits et commandes.
- Créer une API RESTful pour exposer des KPI et des analyses avancées.
- Visualiser ces KPI à travers un tableau de bord interactif.

---

## Structure de l’application

L’application est divisée en deux parties principales :

1. **Backend** :
   - Développé avec le framework Python **FastAPI**.
   - Gère les données et les calculs via **MongoDB**.
   - Expose des endpoints pour fournir des KPI et des analyses avancées.

2. **Frontend** :
   - Conçu avec **Streamlit**.
   - Présente les analyses et visualisations à travers un tableau de bord interactif conçu avec Streamlit et Plotly.

---

## Fonctionnalités principales

1. **Analyse des ventes** :
   - Total des ventes globales, par région, par produit, et par catégorie.

2. **Analyse des profits** :
   - Profits par produit et par catégorie.
   - Identification des éléments les plus rentables.

3. **Segmentation des clients (RFM)** :
   - Classification des clients en segments (Champions, Clients récents, Clients à risque, etc.).

4. **Prévisions** :
   - Utilisation de Facebook Prophet pour prévoir les ventes futures.

5. **Tableau de bord interactif** :
   - Permet une exploration visuelle des données grâce à des graphiques et des indicateurs clairs.

---

## Prérequis

Avant de commencer, assurez-vous d’avoir :

- **Python 3.8+ installé.**
- **MongoDB installé (avec MongoDB Compass pour une interface graphique).**

---

## Étapes d'installation et de configuration

### 1. **Cloner le projet**

Téléchargez le projet depuis GitHub :

```bash
git clone <URL_DU_RÉPÔT>
cd backend_python
```

### 2. **Créer et configurer un environnement Python**

Créer un environnement virtuel :

```bash
python -m venv env
```

Activer l’environnement virtuel :

- **Sur Windows** :

```bash
env\Scripts\activate
```

- **Sur macOS/Linux** :

```bash
source env/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Cela installera toutes les bibliothèques nécessaires, comme FastAPI, Streamlit, Pandas, et Prophet.

---

### 3. **Configurer MongoDB**

#### 3.1 Installer MongoDB

- Téléchargez MongoDB depuis [mongodb.com](https://www.mongodb.com/) et installez-le.
- Installez également MongoDB Compass, une interface graphique pour gérer les bases de données.

#### 3.2 Importer les fichiers CSV dans MongoDB avec Compass

1. Ouvrez MongoDB Compass et connectez-vous à :

   ```plaintext
   mongodb://localhost:27017
   ```

2. Créez une nouvelle base de données appelée **ecommerce**.
3. Dans cette base, créez les collections suivantes :

   - **Orders**
   - **Customers**
   - **Products**

4. Pour chaque collection :

   - Cliquez sur "Import Data".
   - Sélectionnez les fichiers CSV correspondants (par exemple, `orders.csv` pour **Orders**).
   - MongoDB Compass importera automatiquement les données.

---

### 4. **Lancer le projet**

#### 4.1 Démarrer le backend (FastAPI)

1. Ouvrez une invite de commande dans le dossier `backend_python`.
2. Lancez le serveur FastAPI avec :

   ```bash
   uvicorn main:app --reload
   ```

3. Accédez à [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) pour explorer les endpoints de l’API.

#### 4.2 Démarrer le frontend (Streamlit)

1. Dans un nouveau terminal, activez l’environnement virtuel :

   ```bash
   env\Scripts\activate
   ```

   ```bash
   source env/bin/activate
   ```

2. Lancez l’application Streamlit :

   ```bash
   streamlit run app.py
   ```

3. Le tableau de bord s’ouvrira automatiquement dans votre navigateur à [http://localhost:8501](http://localhost:8501).

---

## Création de pipelines d’agrégation avec MongoDB

### 1. **Qu'est-ce qu'un pipeline d'agrégation ?**

Les pipelines d'agrégation de MongoDB permettent de regrouper, transformer et analyser les données en plusieurs étapes. Ils sont utiles pour créer des statistiques ou des KPI avancés à partir de vos collections MongoDB.

---

### 2. **Exemple de pipeline d'agrégation : Analyse des ventes**

Voici un exemple de pipeline pour calculer le total des ventes par produit :

```json
[
  {
    "$group": {
      "_id": "$product_id",
      "total_sales": { "$sum": "$sales" }
    }
  },
  {
    "$sort": { "total_sales": -1 }
  }
]
```

Ce pipeline :
- Regroupe les documents par `product_id`.
- Calcule la somme des ventes (`sales`) pour chaque produit.
- Trie les produits par ventes totales de manière décroissante.

---

### 3. **Utiliser les pipelines avec Python**

Pour connecter MongoDB et exécuter un pipeline avec Python, utilisez la bibliothèque `pymongo`.

#### **Exemple de connexion et exécution** :

```python
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["ecommerce"]

# Définir le pipeline d'agrégation
pipeline = [
    {"$group": {"_id": "$product_id", "total_sales": {"$sum": "$sales"}}},
    {"$sort": {"total_sales": -1}}
]

# Exécuter le pipeline sur la collection "Orders"
results = db["Orders"].aggregate(pipeline)

# Afficher les résultats
for result in results:
    print(result)
```

---

### 4. **Intégration avec FastAPI**

Pour exposer les résultats du pipeline d’agrégation via une API FastAPI :

#### **Exemple d'endpoint FastAPI** :

```python
from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI()

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["ecommerce"]

@app.get("/kpi/total-sales")
def get_total_sales():
    pipeline = [
        {"$group": {"_id": "$product_id", "total_sales": {"$sum": "$sales"}}},
        {"$sort": {"total_sales": -1}}
    ]
    results = list(db["Orders"].aggregate(pipeline))
    return results
```

Avec cet endpoint, vous pouvez accéder au KPI `total-sales` via `http://127.0.0.1:8000/kpi/total-sales`.


## Structure du projet

Voici les fichiers et dossiers principaux :

- **`app.py`** : Code du frontend pour le tableau de bord interactif avec Streamlit.
- **`main.py`** : Backend pour gérer les API avec FastAPI.
- **`pipelines.py`** : Pipelines MongoDB pour regrouper, nettoyer, et transformer les données.
- **`requirements.txt`** : Liste des dépendances nécessaires au projet.
- **`model_rfm.pkl`** : Modèle de segmentation RFM enregistré.
- **`data/`** : Dossier contenant les fichiers CSV à importer dans MongoDB.

---


