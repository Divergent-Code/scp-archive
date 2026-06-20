"""
SCP Wiki Scraper - Crawls the SCP Foundation Wiki and extracts article data.
Target: scp-wiki.wikidot.com
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
from urllib.parse import urljoin
from models import SCPEntry
from wikidot_parser import WikidotParser

BASE_URL = "https://scp-wiki.wikidot.com"
HEADERS = {
    "User-Agent": "SCP-Archive/1.0 (Educational/Research Project; +https://github.com/scp-archive)"
}
DELAY = 1.5  # Polite delay between requests


class SCPScraper:
    """Scrapes the SCP Foundation Wiki."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.entries: list[SCPEntry] = []
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.parser = WikidotParser()
        os.makedirs(data_dir, exist_ok=True)

    def _request(self, url: str) -> BeautifulSoup:
        """Make a request with rate limiting."""
        time.sleep(DELAY)
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")

    def _extract_rating(self, soup: BeautifulSoup) -> int:
        """Extract page rating from Wikidot."""
        rate_points = soup.find("span", class_="rate-points")
        if rate_points:
            number_span = rate_points.find("span", class_="number")
            if number_span:
                try:
                    return int(number_span.get_text(strip=True).lstrip("+"))
                except ValueError:
                    pass
        return 0

    def _extract_tags(self, soup: BeautifulSoup) -> list[str]:
        """Extract tags from the page."""
        tags = []
        tag_div = soup.find("div", class_="page-tags")
        if tag_div:
            for tag_a in tag_div.find_all("a"):
                tag_text = tag_a.get_text(strip=True)
                if tag_text:
                    tags.append(tag_text.lower())
        return tags

    def _extract_attribution(self, soup: BeautifulSoup) -> tuple[str | None, str | None, str | None]:
        """Extract (author, license, source_url) from the licensebox."""
        licensebox = soup.find(class_="licensebox")
        if not licensebox:
            return None, None, None

        text = licensebox.get_text(separator=" ", strip=True)

        author = None
        m = re.search(r'["“][^"”]+["”]\s+by\s+([^,\.]+)', text)
        if m:
            author = m.group(1).strip()

        license_str = None
        m = re.search(r'Licensed under\s+([A-Z][^\.\n]+?)(?:\.|$)', text)
        if m:
            license_str = m.group(1).strip()

        source_url = None
        m = re.search(r'Source:\s*(https?://\S+)', text)
        if m:
            source_url = m.group(1).rstrip(".")

        return author, license_str, source_url

    def _extract_object_class(self, soup: BeautifulSoup) -> str | None:
        """Extract the object class from the page content."""
        # Look for standard Object Class patterns
        content_div = soup.find("div", id="page-content")
        if not content_div:
            return None

        text = content_div.get_text()

        # Common object class patterns
        classes = ["Safe", "Euclid", "Keter", "Thaumiel", "Apollyon",
                   "Archon", "Neutralized", "Explained", "Decommissioned",
                   "Pending", "Esoteric", "Unknown", "Unclassed"]
        
        # Look for "Object Class: <classname>" pattern
        for cls in classes:
            pattern = re.compile(
                rf'(?:Object\s+Class|ObjectClass|object\s+class)\s*[:：]\s*{re.escape(cls)}',
                re.IGNORECASE
            )
            if pattern.search(text):
                return cls

        # Check for [[module Rate]] or other rating modules
        return None

    def _extract_secondary_class(self, content_text: str) -> str | None:
        """Extract secondary class if present."""
        patterns = [
            r'Secondary\s+Class\s*[:：]\s*(\w+)',
            r'SecondaryClass\s*[:：]\s*(\w+)',
        ]
        for p in patterns:
            match = re.search(p, content_text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_containment_procedures(self, content_text: str) -> str:
        """Extract Special Containment Procedures."""
        # Look for section headers like "Special Containment Procedures:"
        patterns = [
            r'Special\s+Containment\s+Procedures?\s*[:：]\s*(.+?)(?=\n\n\w|\Z)',
            r'Containment\s+Procedures?\s*[:：]\s*(.+?)(?=\n\n\w|\Z)',
        ]
        for p in patterns:
            match = re.search(p, content_text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_description(self, content_text: str) -> str:
        """Extract Description section."""
        match = re.search(
            r'(?:Description|Details)\s*[:：]\s*(.+?)(?=\n\n(?:Special\s+Containment|\w+\s*[:：]\s*\n)|\Z)',
            content_text, re.DOTALL | re.IGNORECASE
        )
        if match:
            return match.group(1).strip()
        return content_text[:500] if content_text else ""

    def _find_related_scps(self, content_text: str) -> list[str]:
        """Find references to other SCPs in the content."""
        matches = re.findall(r'SCP-\d+', content_text)
        seen = set()
        result = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                result.append(m)
        return result

    def _extract_created_date(self, soup: BeautifulSoup) -> str | None:
        """Extract the created/last edited date."""
        # Look for Wikidot's ODate module output
        date_patterns = soup.find_all(string=re.compile(r'\d{2}\s+\w+\s+\d{4}'))
        for text in date_patterns:
            match = re.search(r'(\d{2}\s+\w+\s+\d{4})', text)
            if match:
                return match.group(1)
        return None

    def scrape_article(self, url: str, entry_id: str | None = None) -> SCPEntry | None:
        """Scrape a single SCP article."""
        try:
            soup = self._request(url)
            content_div = soup.find("div", id="page-content")

            if not content_div:
                print(f"  [!] No content found at {url}")
                return None

            # Extract title from #page-title div (avoids " - SCP Foundation" suffix)
            page_title_div = soup.find("div", id="page-title")
            if page_title_div:
                title = page_title_div.get_text(strip=True)
            else:
                title_tag = soup.find("title")
                raw = title_tag.get_text(strip=True) if title_tag else ""
                title = re.sub(r"\s*-\s*SCP Foundation$", "", raw).strip() or entry_id or url

            # Get raw content text for parsing
            raw_content = str(content_div)
            content_text = content_div.get_text()

            # Parse to HTML
            content_html = self.parser.parse_wikidot(raw_content)

            # Extract metadata
            rating = self._extract_rating(soup)
            tags = self._extract_tags(soup)
            author, license_str, source_url = self._extract_attribution(soup)
            object_class = self._extract_object_class(soup)
            secondary_class = self._extract_secondary_class(content_text)
            containment = self._extract_containment_procedures(content_text)
            description = self._extract_description(content_text)
            related = self._find_related_scps(content_text)
            created_date = self._extract_created_date(soup)

            # Determine entry type
            entry_type = "scp"
            if "/tale/" in url:
                entry_type = "tale"
            elif "/goi-" in url.lower():
                entry_type = "goi-format"

            entry = SCPEntry(
                id=entry_id or url.split("/")[-1],
                title=title,
                url=url,
                object_class=object_class,
                secondary_class=secondary_class,
                containment_procedures=containment,
                description=description,
                tags=tags,
                author=author,
                rating=rating,
                created_date=created_date,
                entry_type=entry_type,
                related_scps=related,
                content_html=content_html,
                content_md=content_text,
                license=license_str,
                source_url=source_url or url,
            )

            print(f"  [+] Scraped: {entry.id} - {entry.title}")
            return entry

        except Exception as e:
            print(f"  [!] Error scraping {url}: {e}")
            return None

    def _scrape_series_page(self, series_num: int) -> list[str]:
        """Get all SCP URLs from a series page."""
        series_url = f"{BASE_URL}/scp-series-{series_num}"
        if series_num == 1:
            series_url = f"{BASE_URL}/scp-series"
        
        print(f"\n[>] Fetching Series {series_num}...")
        try:
            soup = self._request(series_url)
            # Content pages are usually in a list
            content = soup.find("div", id="page-content")
            urls = []
            if content:
                for a_tag in content.find_all("a", href=True):
                    href = a_tag["href"]
                    # Match SCP article links
                    if re.match(r'^/scp-\d+', href):
                        full_url = urljoin(BASE_URL, href)
                        if full_url not in urls:
                            urls.append(full_url)
            print(f"  [>] Found {len(urls)} SCPs in Series {series_num}")
            return urls
        except Exception as e:
            print(f"  [!] Error fetching series page: {e}")
            return []

    def scrape_series(self, start: int = 1, end: int = 9) -> list[SCPEntry]:
        """Scrape SCP series 1 through N."""
        all_urls = []
        for i in range(start, end + 1):
            urls = self._scrape_series_page(i)
            all_urls.extend(urls)

        print(f"\n[*] Scraping {len(all_urls)} SCP articles from Series {start}-{end}...")
        for url in all_urls:
            entry_id = url.split("/")[-1]
            entry = self.scrape_article(url, entry_id)
            if entry:
                self.entries.append(entry)

        self.save_all()
        return self.entries

    def scrape_tag_page(self, tag: str, entry_type: str = "tale") -> list[SCPEntry]:
        """Scrape all entries with a specific tag (used for tales and GOI formats)."""
        url = f"{BASE_URL}/system:page-tags/tag/{tag}"
        print(f"\n[>] Fetching {tag} pages...")
        
        try:
            soup = self._request(url)
            content = soup.find("div", id="page-content")
            urls = []
            if content:
                for a_tag in content.find_all("a", href=True):
                    href = a_tag["href"]
                    if href.startswith("/") and ":" not in href and "/system:" not in href:
                        full_url = urljoin(BASE_URL, href)
                        urls.append(full_url)

            print(f"  [>] Found {len(urls)} {tag} entries")
            for url in urls:
                entry_id = url.split("/")[-1]
                entry = self.scrape_article(url, entry_id)
                if entry:
                    entry.entry_type = entry_type
                    self.entries.append(entry)

            self.save_all()
            return self.entries
        except Exception as e:
            print(f"  [!] Error fetching {tag}: {e}")
            return []

    def scrape_tales(self) -> list[SCPEntry]:
        """Scrape SCP Foundation tales."""
        return self.scrape_tag_page("tale")

    def scrape_goi_formats(self) -> list[SCPEntry]:
        """Scrape Groups of Interest format pages."""
        return self.scrape_tag_page("goi-format")

    def save_all(self, filename: str = "scp_archive.json"):
        """Save all scraped entries to a JSON file."""
        filepath = os.path.join(self.data_dir, filename)
        data = [e.to_dict() for e in self.entries]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n[*] Saved {len(data)} entries to {filepath}")
        return filepath

    def load(self, filename: str = "scp_archive.json"):
        """Load previously scraped entries."""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            print(f"[!] No saved data found at {filepath}")
            return []
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.entries = [SCPEntry.from_dict(d) for d in data]
        print(f"[*] Loaded {len(self.entries)} entries from {filepath}")
        return self.entries


def main():
    """Main entry point for the scraper."""
    scraper = SCPScraper()
    
    print("=" * 60)
    print("  SCP Foundation Archive Scraper")
    print("=" * 60)

    # Scrape SCP series 1-3 first (smaller test)
    # For a full archive, change to scrape_series(1, 9)
    scraper.scrape_series(1, 3)
    
    # Uncomment to scrape tales and GOI formats
    # scraper.scrape_tales()
    # scraper.scrape_goi_formats()

    print(f"\n[*] Done! Total entries: {len(scraper.entries)}")


if __name__ == "__main__":
    main()