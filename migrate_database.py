#!/usr/bin/env python3
"""
Script de migration pour mettre à jour la base de données existante 
avec les nouvelles fonctionnalités
"""

import sqlite3
import os
from db import get_conn

def migrate_database():
    """Met à jour la base de données avec les nouvelles colonnes et tables"""
    print("Migration de la base de données...")
    
    conn = get_conn()
    c = conn.cursor()
    
    try:
        # Ajouter les nouvelles colonnes à la table orders
        try:
            c.execute("ALTER TABLE orders ADD COLUMN discount_percent REAL DEFAULT 0")
            print("✓ Ajout colonne orders.discount_percent")
        except sqlite3.OperationalError:
            print("- Colonne orders.discount_percent déjà existante")
        
        try:
            c.execute("ALTER TABLE orders ADD COLUMN discount_amount REAL DEFAULT 0")
            print("✓ Ajout colonne orders.discount_amount")
        except sqlite3.OperationalError:
            print("- Colonne orders.discount_amount déjà existante")
        
        try:
            c.execute("ALTER TABLE orders ADD COLUMN currency_id INTEGER REFERENCES currencies(id) DEFAULT 1")
            print("✓ Ajout colonne orders.currency_id")
        except sqlite3.OperationalError:
            print("- Colonne orders.currency_id déjà existante")
        
        # Ajouter la nouvelle colonne à la table order_items
        try:
            c.execute("ALTER TABLE order_items ADD COLUMN discount_percent REAL DEFAULT 0")
            print("✓ Ajout colonne order_items.discount_percent")
        except sqlite3.OperationalError:
            print("- Colonne order_items.discount_percent déjà existante")
        
        # Créer les nouvelles tables si elles n'existent pas
        c.execute("""
            CREATE TABLE IF NOT EXISTS currencies(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                exchange_rate REAL NOT NULL DEFAULT 1.0,
                active INTEGER NOT NULL DEFAULT 1
            )
        """)
        print("✓ Table currencies créée ou vérifiée")
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS table_transfers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES orders(id),
                from_table_id INTEGER NOT NULL REFERENCES tables(id),
                to_table_id INTEGER NOT NULL REFERENCES tables(id),
                transferred_at TEXT NOT NULL,
                user_id INTEGER REFERENCES users(id)
            )
        """)
        print("✓ Table table_transfers créée ou vérifiée")
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS inventory(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL REFERENCES products(id),
                current_stock INTEGER NOT NULL DEFAULT 0,
                min_stock INTEGER NOT NULL DEFAULT 0,
                max_stock INTEGER NOT NULL DEFAULT 100,
                last_updated TEXT NOT NULL
            )
        """)
        print("✓ Table inventory créée ou vérifiée")
        
        # Insérer les devises par défaut si la table est vide
        count = c.execute("SELECT COUNT(*) FROM currencies").fetchone()[0]
        if count == 0:
            currencies = [
                ("EUR", "Euro", "€", 1.0),
                ("USD", "Dollar US", "$", 1.1),
                ("XOF", "Franc CFA", "CFA", 655.957)
            ]
            
            for code, name, symbol, rate in currencies:
                c.execute("INSERT INTO currencies(code,name,symbol,exchange_rate) VALUES(?,?,?,?)",
                         (code, name, symbol, rate))
            print("✓ Devises par défaut ajoutées")
        
        # Initialiser l'inventaire pour les produits existants
        c.execute("""
            INSERT OR IGNORE INTO inventory (product_id, current_stock, min_stock, max_stock, last_updated)
            SELECT p.id, 50, 10, 100, datetime('now')
            FROM products p
            WHERE p.active = 1 
            AND p.id NOT IN (SELECT DISTINCT product_id FROM inventory WHERE product_id IS NOT NULL)
        """)
        
        inserted = c.rowcount
        if inserted > 0:
            print(f"✓ {inserted} produits ajoutés à l'inventaire")
        
        conn.commit()
        print("\n✅ Migration terminée avec succès!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de la migration: {e}")
        raise
    finally:
        conn.close()

def backup_database():
    """Crée une sauvegarde de la base de données"""
    if os.path.exists("pos.db"):
        import shutil
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pos_backup_{timestamp}.db"
        
        shutil.copy2("pos.db", backup_name)
        print(f"✓ Sauvegarde créée: {backup_name}")
        return backup_name
    return None

def main():
    print("=== Migration Base de Données POS ===")
    print()
    
    # Créer une sauvegarde
    backup_file = backup_database()
    
    # Effectuer la migration
    try:
        migrate_database()
        
        print("\nLa base de données a été mise à jour avec succès!")
        print("Nouvelles fonctionnalités disponibles:")
        print("- Support multi-devises")
        print("- Remises sur articles et factures")
        print("- Transferts de table")
        print("- Gestion de l'inventaire")
        print("- Impression PDF de factures")
        
        if backup_file:
            print(f"\nSauvegarde disponible: {backup_file}")
            
    except Exception as e:
        print(f"\n❌ Migration échouée: {e}")
        if backup_file:
            print(f"Vous pouvez restaurer la sauvegarde: {backup_file}")

if __name__ == "__main__":
    main()
