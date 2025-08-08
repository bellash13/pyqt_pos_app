
# POS Buvette/Restaurant (PyQt5 + SQLite)

Un logiciel de gestion de buvette/restaurant : tables numérotées, serveurs, POS (produits par catégories), facturation par table et par serveur, rapports, et gestion des données. Authentification avec rôles (admin, caissier).

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install PyQt5
```
*(Aucune autre dépendance n'est nécessaire.)*

## Lancement
```bash
python app.py
```

- Identifiants par défaut :
  - **Admin** : `admin` / `admin123`
  - **Caissier** : `caissier` / `caissier123`

> Changez les mots de passe depuis **Admin → Utilisateurs**.

## Fonctionnalités
- Connexion (admin/caissier)
- Écran POS : sélection table + serveur, liste des produits par catégories (clic = ajoute à la facture), +/- quantité, suppression de ligne, total, clôture facture.
- Factures par table & par serveur, avec filtre dates.
- Gestion (Admin) : catégories, produits, tables, serveurs, utilisateurs.
- Thème visuel (QSS) simple et propre.
