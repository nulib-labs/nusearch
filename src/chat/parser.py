from dataclasses import dataclass
from typing import Dict, List
from enum import Enum
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

    
def parse_nul_search(data: Dict) -> List[Dict]:
    """Parse the NUL search results and return a list of SearchResult objects."""
    results = []
    for item in data.get("docs", []):
        pnx = item.get("pnx", {})
        display = pnx.get("display", {})

        title = display.get("title", "")
        creators = display.get("creator", [""]) if display.get("creator") else [""]
        publisher = (
            display.get("publisher", [""])[0] if display.get("publisher") else ""
        )
        pub_year = ""
        if display.get("creationdate"):
            year_str = display.get("creationdate")[0]
            import re

            year_match = re.search(r"\b(19|20)\d{2}\b", year_str)
            if year_match:
                pub_year = year_match.group(0)
        container = (
            display.get("ispartof", [""])[0] if display.get("ispartof") else ""
        )
        record_id = pnx.get("control", {}).get("recordid", [""])[0]
        link = f"https://search.library.northwestern.edu/permalink/01NWU_INST/p285fv/{record_id}"
    
        results.append({
            "title": title,
            "creators": creators,
            "publisher": publisher,
            "pub_year": pub_year,
            "container": container,
            "record_id": record_id,
            "link": link
        })

    return results

def parse_digital_collections(content: str) -> List[str]:
    """Parse the digital collections response and return a list of IIIF URLs."""
    iiif_urls = []
    for item in content['items']:
        if 'id' in item:
            iiif_urls.append(item['id'])
    
    return iiif_urls

def parse_open_alex(content: List[Dict]) -> List[Dict]:
    """Parse the OpenAlex response and return a list of citations."""
    """
    [{"id": "https://openalex.org/W380827849", "title": "Willie Mays: My life in and out of baseball", "publication_year": 1972, "language": "en", "authorships": [{"author_position": "first", "author": {"id": "https://openalex.org/A5071265693", "display_name": "Willie Mays", "orcid": null}, "institutions": [], "countries": [], "is_corresponding": false, "raw_author_name": "Willie Mays", "raw_affiliation_strings": [], "affiliations": []}, {"author_position": "last", "author": {"id": "https://openalex.org/A5039460499", "display_name": "Charles Einstein", "orcid": null}, "institutions": [], "countries": [], "is_corresponding": false, "raw_author_name": "Charles Einstein", "raw_affiliation_strings": [], "affiliations": []}]}, {"id": "https://openalex.org/W2118339787", "title": "Baseball's Great Experiment: Jackie Robinson and His Legacy.", "publication_year": 1984, "language": "en", "authorships": [{"author_position": "first", "author": {"id": "https://openalex.org/A5052562198", "display_name": "Jeffrey T. Sammons", "orcid": null}, "institutions": [], "countries": [], "is_corresponding": false, "raw_author_name": "Jeffrey T. Sammons", "raw_affiliation_strings": [], "affiliations": []}, {"author_position": "last", "author": {"id": "https://openalex.org/A5054653374", "display_name": "Jules Tygiel", "orcid": null}, "institutions": [], "countries": [], "is_corresponding": false, "raw_author_name": "Jules Tygiel", "raw_affiliation_strings": [], "affiliations": []}]}, {"id": "https://openalex.org/W1515371796", "title": "Summergame", "publication_year": 2020, "language": "en", "authorships": [{"author_position": "first", "author": {"id": "https://openalex.org/A5097252411", "display_name": "Roger Angell", "orcid": null}, "institutions": [], "countries": [], "is_corresponding": true, "raw_author_name": "Roger Angell", "raw_affiliation_strings": [], "affiliations": []}]}, {"id": "https://openalex.org/W1527111069", "title": "The biographical encyclopedia of the Negro baseball leagues", "publication_year": 1994, "language": "en", "authorships": [{"author_position": "first", "author": {"id": "https://openalex.org/A5014381140", "display_name": "James A. Riley", "orcid": null}, "institutions": [], "countries": [], "is_corresponding": true, "raw_author_name": "James A. Riley", "raw_affiliation_strings": [], "affiliations": []}]}, {"id": "https://openalex.org/W642025799", "title": "Crossing the line: black major leaguers, 1947-1959", "publication_year": 1995, "language": "en", "authorships": [{"author_position": "first", "author": {"id": "https://openalex.org/A5105498705", "display_name": "Larry Moffi", "orcid": null}, "institutions": [], "countries": [], "is_corresponding": false, "raw_author_name": "Larry Moffi", "raw_affiliation_strings": [], "affiliations": []}, {"author_position": "last", "author": {"id": "https://openalex.org/A5105917473", "display_name": "Jonathan Kronstadt", "orcid": null}, "institutions": [], "countries": [], "is_corresponding": false, "raw_author_name": "Jonathan Kronstadt", "raw_affiliation_strings": [], "affiliations": []}]}]
    """
    citations = []
    for item in content:
        title = item.get("title", "")
        authorships = item.get("authorships", [])
        authors = [author for author in authorships if author.get("author")]
        display_names = [author['author']['display_name'] for author in authors]
        publication_year = item.get("publication_year", "")
        language = item.get("language", "")
        link = item.get("id", "")
        citation = {
            "title": title,
            "publication_year": publication_year,
            "authors": display_names,
            "language": language,
            "link": link
        }
        citations.append(citation)

    return citations
    
