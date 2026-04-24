from pypdf import PdfReader
import io

class ContentExtractor:
    @staticmethod
    def extract_from_pdf(file_bytes):
        text = ""
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"PDF Extraction Error: {e}")
        return text

    @classmethod
    def extract(cls, file_bytes, content_type):
        if "pdf" in content_type:
            return cls.extract_from_pdf(file_bytes)
        else:
            # Fallback for raw text
            try:
                return file_bytes.decode("utf-8")
            except:
                return "Binary content detected (Image OCR currently disabled for stability)"
