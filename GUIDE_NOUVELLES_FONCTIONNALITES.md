# Guide des Nouvelles Fonctionnalités - POS Buvette/Restaurant

## Résumé des Améliorations

Votre application POS a été enrichie avec 5 nouvelles fonctionnalités majeures qui transforment votre système basique en une solution professionnelle complète.

## 🎯 Fonctionnalités Ajoutées

### 1. 📄 Impression PDF de Factures
**Localisation :** Interface POS → Bouton "Imprimer PDF"

**Fonctionnalités :**
- Génération automatique de factures PDF professionnelles
- Mise en page complète avec en-tête restaurant, détails commande, calculs
- Ouverture automatique du PDF généré
- Archivage automatique des factures

**Utilisation :**
1. Ouvrez une commande dans le POS
2. Cliquez sur "Imprimer PDF"
3. Le PDF s'ouvre automatiquement et est sauvegardé

### 2. 💰 Système de Remises
**Localisation :** Interface POS → Boutons "Remise" et "Remise Facture"

**Types de remises :**
- **Remise article** : Pourcentage de 0% à 100% sur un article spécifique
- **Remise facture** : Montant fixe ou pourcentage sur le total de la facture

**Utilisation :**
1. **Remise article** : Sélectionnez un article → Cliquez "Remise" → Saisissez le pourcentage
2. **Remise facture** : Cliquez "Remise Facture" → Choisissez type et valeur

### 3. 🌍 Support Multi-Devises
**Localisation :** Interface POS → Sélecteur de devise / Admin → Devises

**Devises par défaut :**
- EUR (Euro) - Taux 1.0
- USD (Dollar US) - Taux 1.1  
- XOF (Franc CFA) - Taux 655.957

**Fonctionnalités :**
- Sélection de devise pour chaque commande
- Taux de change configurables
- Affichage cohérent avec symboles
- Gestion administrative complète

**Utilisation :**
1. Dans le POS, sélectionnez la devise avant de créer une facture
2. Pour gérer les devises : Admin → Devises

### 4. 🔄 Transferts de Table
**Localisation :** Interface POS → Bouton "Transférer Table"

**Fonctionnalités :**
- Transfert de commandes en cours entre tables
- Vérification automatique de disponibilité
- Historique des transferts horodaté
- Mise à jour immédiate de l'interface

**Utilisation :**
1. Ouvrez une commande
2. Cliquez "Transférer Table"
3. Sélectionnez la table de destination
4. Confirmez le transfert

### 5. 📦 Gestion de l'Inventaire
**Localisation :** Onglet "Inventaire" (principal)

**Fonctionnalités :**
- Suivi des stocks en temps réel
- Alertes visuelles (codes couleur)
- Définition de seuils min/max
- Ajustement manuel des stocks
- Initialisation automatique

**Codes couleur :**
- 🟢 **Vert** : Stock OK
- 🟡 **Orange** : Stock faible (≤ minimum)
- 🔴 **Rouge** : Rupture de stock (= 0)

**Utilisation :**
1. Accédez à l'onglet "Inventaire"
2. Sélectionnez un produit et cliquez "Ajuster Stock" pour modifier les quantités
3. Utilisez "Définir Limites" pour configurer les seuils
4. "Initialiser Produits Manquants" pour ajouter de nouveaux produits

## 🛠 Modifications Techniques

### Base de Données
- **Nouvelles tables :** `currencies`, `table_transfers`, `inventory`
- **Nouvelles colonnes :** 
  - `orders` : `discount_percent`, `discount_amount`, `currency_id`
  - `order_items` : `discount_percent`

### Nouveaux Fichiers
- `pdf_generator.py` : Génération des factures PDF
- `views/manage_currencies.py` : Interface de gestion des devises
- `views/inventory_view.py` : Interface de gestion de l'inventaire
- `migrate_database.py` : Script de migration de base de données
- `test_features.py` : Tests de validation des fonctionnalités

### Dépendances Ajoutées
- `reportlab` : Génération des PDF

## 🚀 Migration et Installation

### Pour une nouvelle installation :
```bash
pip install PyQt5 reportlab
python app.py
```

### Pour mise à jour d'une installation existante :
```bash
pip install reportlab
python migrate_database.py
python app.py
```

## 💡 Conseils d'Utilisation

### Workflow Optimisé
1. **Début de service :** Vérifiez l'inventaire
2. **Prise de commande :** Sélectionnez devise, table, serveur
3. **Ajout d'articles :** Utilisez les remises si nécessaire
4. **Transfert :** Utilisez la fonction transfert si le client change de table
5. **Finalisation :** Appliquez remise facture si besoin, imprimez PDF

### Gestion Administrative
- **Quotidien :** Surveillez l'inventaire (alertes visuelles)
- **Hebdomadaire :** Ajustez les stocks selon les réceptions
- **Mensuel :** Révisez les taux de change des devises

### Sauvegardes
- Les factures PDF sont automatiquement sauvegardées
- La base de données est sauvegardée avant migration
- Recommandation : sauvegarde quotidienne de `pos.db`

## 🎓 Formation Équipe

### Pour les Caissiers
- Sélection de devise obligatoire
- Utilisation des remises (formation sur les politiques de remise)
- Transfert de table (procédure simple)
- Impression PDF (automatique)

### Pour les Managers
- Gestion de l'inventaire (alertes et ajustements)
- Configuration des devises et taux
- Supervision des remises appliquées
- Analyse des transferts de tables

## 📞 Support

En cas de problème :
1. Vérifiez que `reportlab` est installé : `pip list | find "reportlab"`
2. Testez les fonctionnalités : `python test_features.py`
3. Consultez les fichiers de sauvegarde en cas de besoin

---

**Votre système POS est maintenant prêt pour un usage professionnel complet !** 🎉
