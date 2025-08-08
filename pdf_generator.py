import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from db import get_conn

class InvoicePDFGenerator:
    def __init__(self):
        self.conn = get_conn()
        
    def generate_invoice(self, order_id, filename=None):
        """Génère une facture PDF pour une commande"""
        try:
            # Récupérer les données de la commande
            order_data = self._get_order_data(order_id)
            if not order_data:
                return False, "Commande introuvable"
            
            # Créer le nom de fichier si non fourni
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"facture_{order_id}_{timestamp}.pdf"
            
            # Créer le PDF
            self._create_pdf(order_data, filename)
            return True, filename
            
        except Exception as e:
            return False, f"Erreur lors de la génération PDF: {str(e)}"
    
    def _get_order_data(self, order_id):
        """Récupère toutes les données nécessaires pour la facture"""
        # Données de base de la commande
        order_query = """
            SELECT o.*, t.number as table_number, t.label as table_label,
                   s.name as server_name, c.symbol as currency_symbol, c.code as currency_code
            FROM orders o
            LEFT JOIN tables t ON o.table_id = t.id
            LEFT JOIN servers s ON o.server_id = s.id
            LEFT JOIN currencies c ON o.currency_id = c.id
            WHERE o.id = ?
        """
        order = self.conn.execute(order_query, (order_id,)).fetchone()
        if not order:
            return None
            
        # Articles de la commande
        items_query = """
            SELECT oi.*, p.name as product_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
            ORDER BY oi.id
        """
        items = list(self.conn.execute(items_query, (order_id,)))
        
        return {
            'order': dict(order),
            'items': [dict(item) for item in items]
        }
    
    def _create_pdf(self, data, filename):
        """Crée le fichier PDF de la facture"""
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # En-tête
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "FACTURE")
        
        # Informations du restaurant
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 80, "Buvette/Restaurant POS")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 100, "123 Rue de la Paix")
        c.drawString(50, height - 115, "12345 Ville")
        c.drawString(50, height - 130, "Tél: +33 1 23 45 67 89")
        
        # Numéro de facture et date
        order = data['order']
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, height - 80, f"Facture N°: {order['id']:06d}")
        c.setFont("Helvetica", 10)
        c.drawString(400, height - 100, f"Date: {order['created_at'][:19]}")
        c.drawString(400, height - 115, f"Table: #{order['table_number']} {order.get('table_label', '')}")
        c.drawString(400, height - 130, f"Serveur: {order['server_name']}")
        
        # Ligne de séparation
        y_pos = height - 160
        c.line(50, y_pos, width - 50, y_pos)
        
        # En-têtes du tableau
        y_pos -= 30
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y_pos, "Désignation")
        c.drawString(300, y_pos, "Prix Unit.")
        c.drawString(370, y_pos, "Qté")
        c.drawString(410, y_pos, "Remise")
        c.drawString(470, y_pos, "Total")
        
        # Ligne sous les en-têtes
        y_pos -= 5
        c.line(50, y_pos, width - 50, y_pos)
        
        # Articles
        y_pos -= 20
        c.setFont("Helvetica", 9)
        total_before_discount = 0
        total_discount = 0
        
        for item in data['items']:
            item_total = item['qty'] * item['price']
            item_discount = item_total * (item.get('discount_percent', 0) / 100)
            item_final = item_total - item_discount
            
            total_before_discount += item_total
            total_discount += item_discount
            
            c.drawString(50, y_pos, item['product_name'][:35])
            c.drawString(300, y_pos, f"{item['price']:.2f}")
            c.drawString(370, y_pos, str(item['qty']))
            c.drawString(410, y_pos, f"{item.get('discount_percent', 0):.1f}%")
            c.drawString(470, y_pos, f"{item_final:.2f}")
            
            y_pos -= 15
            
            if y_pos < 100:  # Nouvelle page si nécessaire
                c.showPage()
                y_pos = height - 50
        
        # Totaux
        y_pos -= 10
        c.line(50, y_pos, width - 50, y_pos)
        y_pos -= 20
        
        c.setFont("Helvetica", 10)
        c.drawString(400, y_pos, f"Sous-total: {total_before_discount:.2f} {order.get('currency_symbol', '€')}")
        y_pos -= 15
        
        if total_discount > 0:
            c.drawString(400, y_pos, f"Remise articles: -{total_discount:.2f} {order.get('currency_symbol', '€')}")
            y_pos -= 15
        
        order_discount = order.get('discount_amount', 0) or 0
        if order_discount > 0:
            c.drawString(400, y_pos, f"Remise facture: -{order_discount:.2f} {order.get('currency_symbol', '€')}")
            y_pos -= 15
        
        final_total = total_before_discount - total_discount - order_discount
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, y_pos, f"TOTAL: {final_total:.2f} {order.get('currency_symbol', '€')}")
        
        # Pied de page
        c.setFont("Helvetica", 8)
        c.drawString(50, 50, "Merci de votre visite !")
        c.drawString(50, 35, f"Facture générée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        
        c.save()
