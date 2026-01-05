"""
Web Loader Service - Fetches and processes content from URLs.
Handles content fetching, parsing, and chunking for retrieval.
"""
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class WebLoader:
    """Service for loading and processing web content."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        timeout: int = 10
    ):
        """
        Initialize WebLoader.
        
        Args:
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
            timeout: Request timeout in seconds
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.timeout = timeout
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def fetch_url(self, url: str) -> Optional[str]:
        """
        Fetch content from a URL.
        
        Args:
            url: The URL to fetch
            
        Returns:
            Raw HTML content or None if fetch fails
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """
        Parse HTML and extract structured content.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary with title, text, and metadata
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.string
            elif soup.find('h1'):
                title = soup.find('h1').get_text()
            
            # Extract main content
            # Remove navigation, footer, etc.
            for tag in soup.find_all(['nav', 'footer', 'aside']):
                tag.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up excessive whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            clean_text = '\n'.join(lines)
            
            return {
                "url": url,
                "title": title,
                "text": clean_text,
                "domain": urlparse(url).netloc
            }
        except Exception as e:
            logger.error(f"Error parsing HTML from {url}: {str(e)}")
            return {
                "url": url,
                "title": "Unknown",
                "text": "",
                "domain": urlparse(url).netloc
            }
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into chunks.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to chunks
            
        Returns:
            List of chunks with metadata
        """
        try:
            chunks = self.text_splitter.split_text(text)
            return [
                {
                    "content": chunk,
                    "metadata": metadata,
                    "chunk_index": i
                }
                for i, chunk in enumerate(chunks)
            ]
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            return [{
                "content": text,
                "metadata": metadata,
                "chunk_index": 0
            }]
    
    def load_urls(self, urls: List[str]) -> Dict[str, Any]:
        """
        Load and process multiple URLs.
        
        Args:
            urls: List of URLs to load
            
        Returns:
            Dictionary with loaded content and chunks
        """
        loaded_content = {}
        all_chunks = []
        
        for url in urls:
            if not url or not url.strip():
                continue
            
            url = url.strip()
            logger.info(f"Loading URL: {url}")
            
            # Fetch content
            html = self.fetch_url(url)
            if not html:
                logger.warning(f"Failed to fetch {url}")
                continue
            
            # Parse HTML
            parsed = self.parse_html(html, url)
            if not parsed["text"]:
                logger.warning(f"No text content extracted from {url}")
                continue
            
            loaded_content[url] = parsed
            
            # Chunk the content
            chunks = self.chunk_text(
                parsed["text"],
                {
                    "url": url,
                    "title": parsed["title"],
                    "domain": parsed["domain"]
                }
            )
            all_chunks.extend(chunks)
        
        return {
            "loaded_content": loaded_content,
            "chunks": all_chunks,
            "total_chunks": len(all_chunks),
            "urls_processed": len(loaded_content)
        }


def load_urls(urls: List[str]) -> Dict[str, Any]:
    """
    Convenience function to load URLs.
    
    Args:
        urls: List of URLs to load
        
    Returns:
        Dictionary with loaded content
    """
    loader = WebLoader()
    return loader.load_urls(urls)
