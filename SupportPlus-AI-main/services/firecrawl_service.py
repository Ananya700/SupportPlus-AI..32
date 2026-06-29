from firecrawl import FirecrawlApp
from core.config import settings

class FirecrawlService:
    def __init__(self):
        self.app = None
        if settings.FIRECRAWL_API_KEY:
            self.app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY)

    def search_web(self, query: str):
        """Search the web for updated troubleshooting steps using Firecrawl."""
        if not self.app:
            return "Firecrawl Service is not initialized. Please set FIRECRAWL_API_KEY."

        try:
            # Note: The search endpoint might require specific parameters depending on Firecrawl API version.
            # Using basic scrape/search if available. 
            # In a real scenario, you might want to scrape specific help pages.
            search_result = self.app.search(
                query=query
            )
            
            # Combine the content from the top results
            content = []
            if search_result and hasattr(search_result, 'web') and search_result.web:
                for item in search_result.web[:3]: # Take top 3 results
                    title = getattr(item, 'title', '')
                    desc = getattr(item, 'description', '')
                    if title or desc:
                        content.append(f"Title: {title}\nDescription: {desc}")
            
            if not content:
                return "No useful troubleshooting steps found on the web."
                
            return "\n\n---\n\n".join(content)
            
        except Exception as e:
            print(f"Error fetching from Firecrawl: {e}")
            return "Failed to retrieve web results due to an error."

firecrawl_service = FirecrawlService()
