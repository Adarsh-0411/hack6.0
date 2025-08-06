import requests
from io import BytesIO
import PyPDF2
from docx import Document as Docx
import pytesseract
from PIL import Image
from typing import List, Dict
from email.parser import BytesParser
from email import policy
from urllib.parse import urlparse
import os

class FileProcessor:
    def __init__(self, chunk_size=512, overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = overlap

    def load_and_process(self, url: str) -> List[Dict]:
        res = requests.get(url)
        if res.status_code != 200:
            raise ValueError("Document download failed.")

        content = BytesIO(res.content)
        path = urlparse(url).path
        _, ext = os.path.splitext(path)

        if ext == '.pdf':
            text = self._from_pdf(content)
        elif ext == '.docx':
            text = self._from_docx(content)
        elif ext == '.eml':
            text = self._from_email(content)
        else:
            raise ValueError("File type not supported")

        return self._split_text(text)

    def _from_pdf(self, content: BytesIO) -> str:
        reader = PyPDF2.PdfReader(content)
        text = "".join([p.extract_text() or "" for p in reader.pages])
        return text if text.strip() else self._ocr_pdf(content)

    def _from_docx(self, content: BytesIO) -> str:
        doc = Docx(content)
        return "\n".join([para.text for para in doc.paragraphs])

    def _from_email(self, content: BytesIO) -> str:
        mail = BytesParser(policy=policy.default).parse(content)
        body = ""
        if mail.is_multipart():
            for part in mail.walk():
                if part.get_content_type() == 'text/plain':
                    body += part.get_content().strip()
        else:
            body = mail.get_content().strip()

        return f"Subject: {mail['subject']}\nFrom: {mail['from']}\n\n{body}"

    def _ocr_pdf(self, content: BytesIO) -> str:
        # Placeholder for OCR
        return ""

    def _split_text(self, text: str) -> List[Dict]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            section = {
                "text": ' '.join(words[i:i+self.chunk_size]),
                "chunk_id": len(chunks),
                "start_index": i,
                "end_index": min(i+self.chunk_size, len(words))
            }
            chunks.append(section)
        return chunks
