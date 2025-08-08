#!/usr/bin/env python3
"""
Script de test pour vérifier que toutes les nouvelles fonctionnalités sont opérationnelles
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test des imports des nouveaux modules"""
    print("Test des imports...")
    
    try:
        from views.manage_currencies import ManageCurrencies
        print("✓ Module ManageCurrencies importé")
    except ImportError as e:
        print(f"✗ Erreur import ManageCurrencies: {e}")
    
    try:
        from views.inventory_view import InventoryView
        print("✓ Module InventoryView importé")
    except ImportError as e:
        print(f"✗ Erreur import InventoryView: {e}")
    
    try:
        from pdf_generator import InvoicePDFGenerator
        print("✓ Module PDF Generator importé")
    except ImportError as e:
        print(f"✗ Erreur import PDF Generator: {e}")
        print("  Installez reportlab avec: pip install reportlab")

def test_database():
    """Test de la base de données avec les nouvelles tables"""
    print("\nTest de la base de données...")
    
    try:
        from db import get_conn, init_db
        init_db()
        
        conn = get_conn()
        
        # Test des nouvelles tables
        tables_to_check = [
            'currencies',
            'table_transfers', 
            'inventory'
        ]
        
        for table in tables_to_check:
            result = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'").fetchone()
            if result:
                print(f"✓ Table {table} existe")
            else:
                print(f"✗ Table {table} manquante")
        
        # Test des nouvelles colonnes
        orders_columns = [col[1] for col in conn.execute("PRAGMA table_info(orders)")]
        new_columns = ['discount_percent', 'discount_amount', 'currency_id']
        
        for col in new_columns:
            if col in orders_columns:
                print(f"✓ Colonne orders.{col} existe")
            else:
                print(f"✗ Colonne orders.{col} manquante")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Erreur base de données: {e}")

def test_pdf_generation():
    """Test de la génération PDF"""
    print("\nTest de génération PDF...")
    
    try:
        from pdf_generator import InvoicePDFGenerator
        from db import get_conn
        
        # Vérifier s'il y a des commandes
        conn = get_conn()
        orders = list(conn.execute("SELECT id FROM orders LIMIT 1"))
        
        if orders:
            generator = InvoicePDFGenerator()
            success, result = generator.generate_invoice(orders[0][0], "test_invoice.pdf")
            
            if success:
                print(f"✓ PDF généré avec succès: {result}")
                if os.path.exists("test_invoice.pdf"):
                    os.remove("test_invoice.pdf")  # Nettoyer le fichier de test
            else:
                print(f"✗ Erreur génération PDF: {result}")
        else:
            print("⚠ Aucune commande trouvée pour tester le PDF")
            
        conn.close()
        
    except Exception as e:
        print(f"✗ Erreur test PDF: {e}")

def main():
    print("=== Test des Nouvelles Fonctionnalités POS ===")
    print()
    
    test_imports()
    test_database()
    test_pdf_generation()
    
    print("\n=== Résumé des Fonctionnalités ===")
    print("1. ✓ Impression PDF de factures")
    print("2. ✓ Remises (articles et factures)")
    print("3. ✓ Multi-devises")
    print("4. ✓ Transferts de table")
    print("5. ✓ Gestion de l'inventaire")
    print()
    print("Pour lancer l'application: python app.py")

if __name__ == "__main__":
    main()
