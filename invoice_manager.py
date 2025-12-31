# invoice_manager.py
# Manages invoice creation, numbering, and exporting.

import os
from datetime import datetime
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch, mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Spacer, Image
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.lib.utils import ImageReader
    import arabic_reshaper
    from bidi.algorithm import get_display
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
except ImportError:
    pass

# Register Arial for decent Arabic support (standard Windows font)
ARABIC_FONT_NAME = "Arial"
try:
    # Try typical Windows path or assume it's system available
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
except:
    # Fallback to Helvetica if Arial not found (won't look good for Arabic but avoids crash)
    print("WARNING: Arial font not found. Arabic may not render.")
    ARABIC_FONT_NAME = "Helvetica"


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
            print("WARNING: sale_data missing invoice_number. This should not happen now.")
            sale_data['invoice_number'] = self.get_next_invoice_number() # Fallback for old sales

        invoice_path = os.path.join(self.invoice_dir, f"{sale_data['invoice_number']}.pdf")
        
        shop_name = settings.get('shop_name', 'SmokeDash')
        currency = settings.get('currency', 'LYD')
        logo_path = settings.get('logo_path', None)
        show_logo = settings.get('show_logo', True)

        try:
            # 1. Prepare Elements & Styles
            page_width = 80 * mm
            margin = 2 * mm
            printable_width = page_width - (2 * margin)
            
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            style_nc = styles['Normal']
            style_nc.fontName = ARABIC_FONT_NAME
            style_nc.fontSize = 10
            style_nc.alignment = TA_CENTER
            style_nc.leading = 12

            style_right = styles['Normal']
            style_right.fontName = ARABIC_FONT_NAME
            style_right.fontSize = 9
            style_right.alignment = TA_RIGHT
            
            style_left = styles['Normal']
            style_left.fontName = ARABIC_FONT_NAME
            style_left.fontSize = 9
            style_left.alignment = TA_LEFT

            def reshape(text):
                try:
                    return get_display(arabic_reshaper.reshape(str(text)))
                except:
                    return str(text)

            # --- Logo ---
            if show_logo and logo_path and os.path.exists(logo_path):
                img = Image(logo_path)
                img.drawHeight = 35 * mm
                img.drawWidth = 35 * mm * (img.imageWidth / img.imageHeight)
                if img.drawWidth > 70 * mm:
                     img.drawWidth = 70 * mm
                     img.drawHeight = 70 * mm * (img.imageHeight / img.imageWidth)
                elements.append(img)
                elements.append(Spacer(1, 5))

            # --- Shop Name ---
            elements.append(Paragraph(reshape(shop_name), style_nc))
            elements.append(Spacer(1, 5))
            
            # --- Invoice Info ---
            elements.append(Paragraph("--------------------------------", style_nc))
            elements.append(Paragraph(f"NO: {sale_data['invoice_number']}", style_nc))
            t_str = sale_data['timestamp'].replace('T', ' ').split('.')[0]
            elements.append(Paragraph(t_str, style_nc))
            
            if customer_data:
                 elements.append(Paragraph(reshape(f"العميل: {customer_data['name']}"), style_nc))
            
            elements.append(Paragraph("--------------------------------", style_nc))
            
            # --- Items Table ---
            data = [[reshape("الإجمالي"), reshape("السعر"), reshape("ع"), reshape("الصنف")]]
            
            for item in sale_data['items']:
                name = reshape(item['name'])
                name_para = Paragraph(name, style_right)
                qty = str(item['quantity'])
                price = f"{item['price']:.2f}"
                total = f"{item['quantity'] * item['price']:.2f}"
                data.append([total, price, qty, name_para])
            
            t = Table(data, colWidths=[18*mm, 15*mm, 8*mm, 34*mm])
            t.setStyle(TableStyle([
                ('FONT', (0,0), (-1,-1), ARABIC_FONT_NAME, 8),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LINEBELOW', (0,0), (-1,0), 1, black),
                ('LINEBELOW', (0,-1), (-1,-1), 0.5, HexColor('#aaaaaa')),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 2),
            ]))
            elements.append(t)
            
            elements.append(Paragraph("--------------------------------", style_nc))
            
            # --- Totals ---
            total_val = f"{sale_data['total_amount']:.2f} {currency}"
            t_data = [
                [total_val, reshape("الإجمالي:")],
                [reshape(sale_data.get('payment_method', '')), reshape("طريقة الدفع:")]
            ]
            t_tot = Table(t_data, colWidths=[40*mm, 35*mm])
            t_tot.setStyle(TableStyle([
                ('FONT', (0,0), (-1,-1), ARABIC_FONT_NAME, 10),
                ('ALIGN', (0,0), (0,-1), 'LEFT'),
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,0), 'Arial-Bold'),
                ('TEXTCOLOR', (0,0), (-1,0), black),
            ]))
            elements.append(t_tot)
            
            elements.append(Paragraph(reshape("شكراً لزيارتكم!"), style_nc))
            elements.append(Spacer(1, 10))
            
            # 2. Calculate Total Height
            total_height = 0
            for elem in elements:
                w, h = elem.wrap(printable_width, 10000) # Wrap with infinite height
                total_height += h
            
            # Add margins
            total_height += (2 * margin) + 10 # Buffer
            
            # 3. Create Document with Calculated Height
            doc = SimpleDocTemplate(invoice_path, pagesize=(page_width, total_height),
                                    rightMargin=margin, leftMargin=margin,
                                    topMargin=margin, bottomMargin=margin)
            
            doc.build(elements)
            print(f"Successfully generated dynamic invoice ({total_height/mm:.1f}mm): {invoice_path}")
            return invoice_path

        except Exception as e:
            print(f"Error generating PDF invoice: {e}")
            import traceback
            traceback.print_exc()
            return None

    def print_invoice(self, pdf_path):
        """
        Prints the specified PDF invoice using the default system printer.
        Uses win32api for better reliability on Windows.
        """
        if not pdf_path or not os.path.exists(pdf_path):
            print(f"Error: Invoice path does not exist: {pdf_path}")
            return

        try:
            if os.name == 'nt': # Windows
                import win32api
                import win32print
                
                # Get default printer to verify it exists
                printer = win32print.GetDefaultPrinter()
                print(f"Printing to default printer: {printer}")
                
                # Use ShellExecute with 'print' verb
                # This is more robust than os.startfile on some systems
                win32api.ShellExecute(0, "print", pdf_path, None, ".", 0)
                print(f"Sent to printer via ShellExecute: {pdf_path}")
            else:
                # Linux/Mac fallback (lp)
                os.system(f"lp {pdf_path}")
                print(f"Sent to printer (lp): {pdf_path}")
        except Exception as e:
            print(f"Error printing invoice: {e}")
            # Final fallback: just try to open it so user can manually print
            try:
                if os.name == 'nt':
                    os.startfile(pdf_path)
                    print("Fallback: Opened PDF for manual printing.")
            except:
                pass


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