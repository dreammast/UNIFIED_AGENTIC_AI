import io
import logging
from typing import Optional, List
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

logger = logging.getLogger(__name__)

class ContentProcessor:
    """
    Service for processing multimodal content (Files, URLs, Images).
    """

    @staticmethod
    def process_file(file_obj) -> str:
        """
        Extracts text from uploaded files (txt, md, pdf).
        Args:
            file_obj: Streamlit UploadedFile object
        Returns:
            str: Extracted text content
        """
        try:
            file_type = file_obj.type
            file_name = file_obj.name.lower()
            
            if "pdf" in file_type or file_name.endswith(".pdf"):
                return ContentProcessor._read_pdf(file_obj)
            elif "text" in file_type or file_name.endswith((".txt", ".md")):
                return file_obj.read().decode("utf-8")
            else:
                return f"[Unsupported file type: {file_name}]"
        
        except Exception as e:
            logger.error(f"Error processing file {file_obj.name}: {e}")
            return f"[Error processing file {file_obj.name}: {str(e)}]"

    @staticmethod
    def _read_pdf(file_obj) -> str:
        """Helper to read PDF files using pypdf."""
        reader = PdfReader(file_obj)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    @staticmethod
    def process_url(url: str) -> str:
        """
        Extracts main text content from a URL.
        Args:
            url (str): The URL to scrape
        Returns:
            str: Extracted text content
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text[:10000] # Limit content length
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            return f"[Error fetching URL {url}: {str(e)}]"

    @staticmethod
    def process_content_list(files: List = None, urls: List[str] = None) -> str:
        """
        Processes a list of files and URLs into a single context string.
        """
        context = ""
        
        if files:
            for file in files:
                content = ContentProcessor.process_file(file)
                context += f"\n--- File: {file.name} ---\n{content}\n"
        
        if urls:
            for url in urls:
                content = ContentProcessor.process_url(url)
                context += f"\n--- URL: {url} ---\n{content}\n"
                
        return context
