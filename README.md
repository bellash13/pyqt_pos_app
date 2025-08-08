
# Système POS Buvette/Restaurant - Version Étendue

Application de point de vente (POS) complète pour restaurants et buvettes, développée avec PyQt5 et SQLite.

## Nouvelles Fonctionnalités Ajoutées

### 1. 📄 Impression PDF de Factures
- Génération automatique de factures en PDF avec reportlab
- Mise en page professionnelle avec en-tête, détails articles, remises et totaux
- Bouton "Imprimer PDF" dans l'interface POS
- Ouverture automatique du PDF généré

### 2. 💰 Système de Remises
- **Remises sur articles individuels** : Pourcentage de remise par ligne
- **Remises sur facture complète** : Montant fixe ou pourcentage sur le total
- Interface intuitive avec dialogues dédiés
- Calcul automatique des totaux avec remises

### 3. 🌍 Support Multi-Devises
- Gestion de plusieurs devises (EUR, USD, XOF par défaut)
- Taux de change configurables
- Sélection de devise pour chaque commande
- Interface d'administration des devises
- Affichage des montants avec symboles de devise

### 4. 🔄 Transferts de Table
- Transfert de commandes entre tables en cours de service
- Historique des transferts avec horodatage
- Vérification de disponibilité des tables de destination
- Interface simple avec sélection de nouvelle table

### 5. 📦 Gestion de l'Inventaire
- Suivi des stocks en temps réel
- Définition de seuils minimum et maximum
- Alerte visuelle pour stocks faibles et ruptures
- Interface d'ajustement des stocks
- Initialisation automatique pour nouveaux produits

## Installation et Démarrage

### Prérequis
```bash
pip install PyQt5 reportlab
```

### Lancement de l'application
```bash
python app.py
```

### Comptes par défaut
- **Admin** : admin / admin123
- **Caissier** : caissier / caissier123

## Structure de l'Application

### Onglets Principaux
1. **POS** : Interface de vente avec nouvelles fonctionnalités
2. **Rapports** : Statistiques et historique
3. **Inventaire** : Gestion des stocks (NOUVEAU)

### Administration (Admin uniquement)
- **Catégories** : Gestion des catégories de produits
- **Produits** : Gestion du catalogue
- **Tables** : Configuration des tables
- **Serveurs** : Gestion du personnel
- **Utilisateurs** : Gestion des comptes
- **Devises** : Configuration des devises (NOUVEAU)

## Fonctionnalités Détaillées

### Interface POS Améliorée
- Sélection de devise pour chaque commande
- Boutons de remise pour articles et facture complète
- Transfert de table en un clic
- Génération PDF immédiate
- Affichage détaillé : sous-total, remises, total final

### Gestion des Remises
- **Article** : Pourcentage de 0% à 100%
- **Facture** : Montant fixe ou pourcentage
- Sauvegarde automatique dans la base de données
- Recalcul en temps réel des totaux

### Système Multi-Devises
- Configuration de devises avec codes, noms et symboles
- Taux de change modifiables
- Activation/désactivation de devises
- Affichage cohérent dans toute l'application

### Inventaire Intelligent
- Codes couleur : Vert (OK), Orange (Faible), Rouge (Rupture)
- Ajustements manuels avec historique
- Initialisation en lot pour nouveaux produits
- Interface intuitive avec légende

### Transferts de Table
- Sélection visuelle de la table de destination
- Vérification automatique de disponibilité
- Enregistrement de l'historique avec horodatage
- Mise à jour immédiate de l'interface

## Génération PDF

Les factures PDF incluent :
- Informations du restaurant
- Numéro de facture et date
- Détails de la table et du serveur
- Liste des articles avec remises
- Calculs de totaux détaillés
- Devise sélectionnée
- Pied de page avec horodatage

## Support et Développement

Cette version étend significativement les capacités du système POS original avec des fonctionnalités demandées par les utilisateurs professionnels.
