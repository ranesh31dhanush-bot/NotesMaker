from fpdf import FPDF
import re

class PDFEngine:
    @staticmethod
    def create_pdf(markdown_content, filename, title):
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=title, ln=True, align='C')
        pdf.ln(10)
        
        # Content
        pdf.set_font("Arial", size=11)
        
        # Super simple markdown to text conversion for basic FPDF
        # Remove bold/italic markers and headers
        clean_text = re.sub(r'#+\s', '', markdown_content) # Headings
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_text) # Bold
        clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text) # Italic
        clean_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', clean_text) # Links
        
        # Fix encoding issues for FPDF (only supports Latin-1 by default)
        clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
        
        for line in clean_text.split('\n'):
            # Use multi_cell for wrapping text
            pdf.multi_cell(0, 8, txt=line)
            
        pdf.output(filename)
        return filename
