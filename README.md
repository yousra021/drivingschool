# Driving School Management System

Système de gestion d'auto-école développé avec Django.

## Prérequis

- Python 3.11
- pipenv (gestionnaire de dépendances Python)
- Node.js et npm (pour les dépendances frontend)

## Installation

### 1. Cloner le projet

```bash
cd drivingschool
```

### 2. Installer les dépendances Python

```bash
pipenv install
```

Cela installera toutes les dépendances Python nécessaires, y compris Django et Stripe.

### 3. Installer les dépendances Node.js

```bash
npm install
```

Cela installera Tailwind CSS et les autres dépendances frontend.

### 4. Configuration de l'environnement

Créez un fichier `.env` à la racine du projet (`drivingschool/`) avec la clé secrète Stripe :

```env
STRIPE_SECRET_KEY=votre_clé_secrète_stripe
```

### 5. Configuration de la base de données

Exécutez les migrations pour créer la structure de la base de données :

```bash
cd drivingschool
pipenv run python manage.py migrate
```

### 6. Charger les données initiales (optionnel)

Si vous avez des fixtures, vous pouvez les charger :

```bash
pipenv run python manage.py loaddata fixtures/initial_data.json
```

### 7. Créer un superutilisateur (optionnel)

Pour accéder à l'interface d'administration Django :

```bash
pipenv run python manage.py createsuperuser
```

## Lancement du projet

### Démarrer le serveur de développement

```bash
cd drivingschool
pipenv run python manage.py runserver
```

Le serveur sera accessible à l'adresse : **http://127.0.0.1:8000/**

### Accès à l'interface d'administration

Si vous avez créé un superutilisateur, vous pouvez accéder à l'interface d'administration à :
**http://127.0.0.1:8000/admin/**

## Structure du projet

- `accounts/` - Gestion des utilisateurs (étudiants, instructeurs, secrétaires)
- `dashboard/` - Tableaux de bord selon les rôles
- `planning/` - Gestion des rendez-vous et des leçons
- `bonus/stripe_payment/` - Intégration des paiements Stripe
- `templates/` - Templates HTML
- `my_driving_school/` - Configuration principale Django

## Commandes utiles

### Créer une nouvelle migration

```bash
pipenv run python manage.py makemigrations
```

### Appliquer les migrations

```bash
pipenv run python manage.py migrate
```

### Accéder au shell Django

```bash
pipenv run python manage.py shell
```

### Collecter les fichiers statiques (pour la production)

```bash
pipenv run python manage.py collectstatic
```

## Notes

- Le projet utilise SQLite comme base de données par défaut
- Le mode DEBUG est activé par défaut (à désactiver en production)
- Assurez-vous d'avoir configuré votre clé Stripe dans le fichier `.env` pour utiliser les fonctionnalités de paiement
