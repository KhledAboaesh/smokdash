# invoice_manager.py
# Manages invoice creation, numbering, and exporting.

import os
from datetime import datetime
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph
    from reportlab.lib.colors import HexColor
except ImportError:
    raise ImportError("ReportLab library not found. Please install it using: pip install reportlab")

# For Arabic text, we need to use a font that supports it.
# This requires a .ttf font file. We'll assume one is available.
# A good open-source choice is 'DejaVuSans'.
# We will check for it and handle potential errors.
ARABIC_FONT_NAME = "DejaVuSans"
try:
    pdfmetrics.registerFont(TTFont(ARABIC_FONT_NAME, 'DejaVuSans.ttf'))
except:
    print("WARNING: DejaVuSans.ttf not found. Arabic text in PDFs may not render correctly.")
    ARABIC_FONT_NAME = "Helvetica" # Fallback


class InvoiceManager:
    """Manages invoice generation, numbering, and PDF export."""

    def __init__(self, data_manager, invoice_dir='invoices'):
        """
        Initializes the InvoiceManager.

        Args:
            data_manager: An instance of DataManager to interact with the database.
            invoice_dir (str): The directory to save PDF invoices.
        """
        self.db = data_manager
        self.invoice_dir = invoice_dir
        os.makedirs(self.invoice_dir, exist_ok=True)

    def get_next_invoice_number(self):
        """
        Generates a new, unique invoice number based on the last sale.
        Format: INV-YYYY-NNNN
        """
        sales = self.db.get_sales()
        today = datetime.now()
        year_prefix = f"INV-{today.year}-"
        
        last_invoice_num = 0
        for sale in sales:
            if sale.get('invoice_number', '').startswith(year_prefix):
                try:
                    num = int(sale['invoice_number'].split('-')[-1])
                    if num > last_invoice_num:
                        last_invoice_num = num
                except (ValueError, IndexError):
                    continue
        
        return f"{year_prefix}{last_invoice_num + 1:04d}"

    def generate_pdf_invoice(self, sale_data, settings, customer_data=None):
        """
        Generates a PDF invoice for a given sale.

        Args:
            sale_data (dict): The dictionary containing sale details.
            settings (dict): Application settings (shop name, currency).
            customer_data (dict, optional): Customer details if it's a debt sale.

        Returns:
            str: The path to the generated PDF file, or None on failure.
        """
        if 'invoice_number' not in sale_data:
            sale_data['invoice_number'] = self.get_next_invoice_number()

        invoice_path = os.path.join(self.invoice_dir, f"{sale_data['invoice_number']}.pdf")
        
        shop_name = settings.get('shop_name', 'SmokeDash')
        currency = settings.get('currency', 'LYD')

        try:
            c = canvas.Canvas(invoice_path, pagesize=letter)
            width, height = letter

            # --- Helper for Arabic text ---
            def draw_arabic_text(text, x, y, size=12, color_hex="#000000"):
                p = Paragraph(text, style=getSampleStyleSheet()['Normal'])
                p.fontName = ARABIC_FONT_NAME
                p.fontSize = size
                p.textColor = HexColor(color_hex)
                p.wrapOn(c, width - 2*inch, height)
                p.drawOn(c, x, y)

            # --- Header ---
            c.setFont(ARABIC_FONT_NAME, 24)
            c.setFillColor(HexColor("#333333"))
            c.drawRightString(width - 1*inch, height - 1*inch, shop_name)
            c.setFont("Helvetica-Bold", 16)
            c.drawRightString(width - 1*inch, height - 1.3*inch, "INVOICE / فاتورة")

            # --- Invoice Info ---
            c.setFont("Helvetica", 10)
            info_y = height - 2 * inch
            c.drawString(1*inch, info_y, f"Invoice #: {sale_data['invoice_number']}")
            sale_time = datetime.fromisoformat(sale_data['timestamp']).strftime('%Y-%m-%d %H:%M')
            c.drawString(1*inch, info_y - 20, f"Date: {sale_time}")
            
            if customer_data:
                c.drawString(1*inch, info_y - 60, "Bill To / العميل:")
                draw_arabic_text(customer_data['name'], 1*inch, info_y - 80, size=10)
                if customer_data.get('phone'):
                    c.drawString(1*inch, info_y - 100, customer_data['phone'])
            
            # --- Table Header ---
            table_y = info_y - 140
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(HexColor("#ffffff"))
            c.rect(1*inch, table_y - 5, width - 2*inch, 25, fill=1, stroke=0)
            c.setFillColor(HexColor("#000000"))
            c.drawRightString(width - 1.2*inch, table_y, "Item / الصنف")
            c.drawRightString(width - 3.5*inch, table_y, "Qty / الكمية")
            c.drawRightString(width - 4.8*inch, table_y, "Unit Price / السعر")
            c.drawRightString(width - 6*inch, table_y, "Total / الإجمالي")

            # --- Table Rows ---
            c.setFont("Helvetica", 10)
            current_y = table_y - 30
            for item in sale_data['items']:
                draw_arabic_text(item['name'], width - 1.2*inch, current_y, size=10)
                c.drawRightString(width - 3.5*inch, current_y, str(item['quantity']))
                c.drawRightString(width - 4.8*inch, current_y, f"{item['price']:.2f}")
                item_total = item['quantity'] * item['price']
                c.drawRightString(width - 6*inch, current_y, f"{item_total:.2f}")
                current_y -= 25

            # --- Total ---
            total_y = current_y - 30
            c.setFont("Helvetica-Bold", 12)
            total_text = f"Total / الإجمالي: {sale_data['total_amount']:.2f} {currency}"
            draw_arabic_text(total_text, width - 1.2*inch, total_y)

            payment_map = {"Cash": "نقداً", "Card": "بطاقة", "Debt": "آجل"}
            payment_text = f"Payment Method: {payment_map.get(sale_data['payment_method'], 'N/A')}"
            draw_arabic_text(payment_text, width - 1.2*inch, total_y - 25, size=10)


            # --- Footer ---
            c.setFont("Helvetica-Oblique", 9)
            c.setFillColor(HexColor("#888888"))
            footer_text = "Thank you for your business! شكراً لتعاملكم معنا!"
            draw_arabic_text(footer_text, width / 2 - c.stringWidth(footer_text, "Helvetica", 9)/2, 0.5*inch)

            c.save()
            print(f"Successfully generated invoice: {invoice_path}")
            return invoice_path
        except Exception as e:
            print(f"Error generating PDF invoice: {e}")
            return None


if __name__ == '__main__':
    # This is a dummy DataManager for testing purposes.
    class DummyDataManager:
        def get_sales(self):
            return [
                {'invoice_number': 'INV-2025-0001', 'timestamp': '2025-12-29T10:00:00'},
                {'invoice_number': 'INV-2025-0002', 'timestamp': '2025-12-29T11:00:00'}
            ]
    
    # Example Usage
    print("--- Testing InvoiceManager ---")
    
    dummy_db = DummyDataManager()
    invoice_mgr = InvoiceManager(dummy_db)
    
    # 1. Get next invoice number
    next_num = invoice_mgr.get_next_invoice_number()
    print(f"\n1. Next invoice number should be INV-2025-0003: {next_num}")
    assert next_num == f"INV-{datetime.now().year}-0003"
    
    # 2. Generate a test PDF
    print("\n2. Generating a test PDF...")
    
    # Dummy data for the PDF
    mock_sale = {
        'id': 'sale_123',
        'timestamp': datetime.now().isoformat(),
        'total_amount': 250.50,
        'payment_method': 'Cash',
        'invoice_number': next_num,
        'items': [
            {'name': 'مالبورو أحمر', 'quantity': 5, 'price': 20.00},
            {'name': 'كوكا كولا', 'quantity': 2, 'price': 2.50},
            {'name': 'L&M Blue', 'quantity': 10, 'price': 14.55},
        ]
    }
    mock_settings = {'shop_name': 'متجر النخبة', 'currency': 'دينار'}
    
    pdf_path = invoice_mgr.generate_pdf_invoice(mock_sale, mock_settings)
    
    if pdf_path and os.path.exists(pdf_path):
        print(f"PDF generated successfully at: {pdf_path}")
        # On Windows, open the file
        if os.name == 'nt':
            try:
                os.startfile(pdf_path)
                print("Opened the PDF for review.")
            except Exception as e:
                print(f"Could not automatically open PDF: {e}")
    else:
        print("PDF generation failed.")
        
    print("\n--- Test complete ---")