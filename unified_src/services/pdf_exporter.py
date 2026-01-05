import io
from fpdf import FPDF
from datetime import datetime

class PDFExporter:
    """
    Universal PDF Exporter for the Agentic AI Platform.
    Handles distinct formats for Reports/Blogs and Chat Histories.
    """
    
    @staticmethod
    def _create_base_pdf(title: str):
        """Creates a PDF object with standard header/footer config."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add fonts (standard Arial for now, can be upgraded to consume ttf)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(5)
        
        # Metadata
        pdf.set_font("Arial", "I", 10)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 10, f"Generated on: {timestamp}", ln=True, align="C")
        pdf.line(10, 30, 200, 30)
        pdf.ln(10)
        
        return pdf

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """
        Sanitizes text for FPDF (latin-1 encoding mostly).
        Replaces common incompatible characters.
        """
        replacements = {
            '\u2013': '-', '\u2014': '-',
            '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"',
            '\u2022': '*',
            '…': '...',
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        
        # Encode to latin-1, replace errors with ? to avoid crash
        return text.encode('latin-1', 'replace').decode('latin-1')

    @staticmethod
    def export_report(title: str, content: str) -> bytes:
        """
        Exports a Markdown-like report/blog post to PDF.
        Simple parser for headers and paragraphs.
        """
        pdf = PDFExporter._create_base_pdf(title)
        pdf.set_font("Arial", size=12)
        
        # Simple Markdown parsing
        lines = content.split('\n')
        for line in lines:
            line = PDFExporter._sanitize_text(line)
            
            if line.startswith('# '):
                # H1
                pdf.set_font("Arial", "B", 16)
                pdf.ln(5)
                pdf.multi_cell(0, 10, line.replace('# ', ''))
                pdf.set_font("Arial", size=12)
            elif line.startswith('## '):
                # H2
                pdf.set_font("Arial", "B", 14)
                pdf.ln(4)
                pdf.multi_cell(0, 10, line.replace('## ', ''))
                pdf.set_font("Arial", size=12)
            elif line.startswith('### '):
                # H3
                pdf.set_font("Arial", "B", 12)
                pdf.ln(3)
                pdf.multi_cell(0, 10, line.replace('### ', ''))
                pdf.set_font("Arial", size=12)
            elif line.startswith('- ') or line.startswith('* '):
                # Bullet point
                pdf.set_x(15) # Indent
                pdf.multi_cell(0, 7, f"\u2022 {line[2:]}")
            else:
                # Regular paragraph
                if line.strip():
                    pdf.multi_cell(0, 7, line)
                else:
                    pdf.ln(5)

        return bytes(pdf.output())

    @staticmethod
    def export_chat_history(title: str, messages: list) -> bytes:
        """
        Exports a list of chat messages to PDF.
        Expects messages to be objects with 'content' or dicts with 'content'.
        """
        pdf = PDFExporter._create_base_pdf(title)
        
        for msg in messages:
            # Determine role and content
            role = "Unknown"
            content = ""
            
            if hasattr(msg, 'type'):
                role = "User" if msg.type == 'human' else "AI"
                content = msg.content
            elif isinstance(msg, dict):
                role = "User" if msg.get('role') == 'user' else "AI"
                content = msg.get('content', '')
            
            # Sanitize
            content = PDFExporter._sanitize_text(content)
            
            # Header
            pdf.set_font("Arial", "B", 11)
            if role == "User":
                pdf.set_text_color(0, 102, 204) # Blue for user
            else:
                pdf.set_text_color(0, 153, 76) # Green for AI
                
            pdf.cell(0, 8, f"{role}:", ln=True)
            
            # Content
            pdf.set_text_color(0, 0, 0) # Black
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 7, content)
            pdf.ln(5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Separator
            pdf.ln(5)

        return bytes(pdf.output())
