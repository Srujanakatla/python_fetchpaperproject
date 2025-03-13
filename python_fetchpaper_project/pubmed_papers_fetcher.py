"""
Module for fetching and filtering research papers from PubMed with industry affiliations.
"""

import re
import csv
import sys
import logging
import argparse
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
import requests
from requests.exceptions import RequestException
from io import StringIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pubmed_papers")

# Constants
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
SEARCH_URL = f"{BASE_URL}/esearch.fcgi"
FETCH_URL = f"{BASE_URL}/efetch.fcgi"
EMAIL_PATTERN = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')

# List of terms that indicate non-academic affiliation
COMPANY_INDICATORS = [
    "Pharma", "Pharmaceutical", "Biotech", "Therapeutics", "Inc", 
    "LLC", "Ltd", "GmbH", "Corp", "Corporation", "Company",
    "Technologies", "Biosciences", "Biopharma", "Labs", "Drug", 
    "Research", "Medicines", "Medical", "Health", "Sciences", 
    "BioMed", "Laboratories"
]

# List of terms that indicate academic affiliation
ACADEMIC_INDICATORS = [
    "University", "College", "Institute", "School", "Academia", 
    "Faculty", "Department", "Hospital", "Clinic", "Medical Center", 
    "Center for", "Laboratory of", "National", "Federal", "State",
    "Ministry", "Government", "Public Health", "Institution"
]

@dataclass
class PaperAuthor:
    """Class to store author details."""
    name: str
    affiliation: str
    email: Optional[str] = None
    is_corresponding: bool = False
    is_non_academic: bool = False
    company_name: Optional[str] = None

@dataclass
class Paper:
    """Class to store paper details."""
    pubmed_id: str
    title: str
    publication_date: str
    authors: List[PaperAuthor]
    
    @property
    def non_academic_authors(self) -> List[PaperAuthor]:
        """Return list of non-academic authors."""
        return [author for author in self.authors if author.is_non_academic]
    
    @property
    def has_non_academic_author(self) -> bool:
        """Check if paper has at least one non-academic author."""
        return any(author.is_non_academic for author in self.authors)
    
    @property
    def corresponding_author_email(self) -> Optional[str]:
        """Return email of corresponding author if available."""
        for author in self.authors:
            if author.is_corresponding and author.email:
                return author.email
        # If no corresponding author found, return email of first author with email
        for author in self.authors:
            if author.email:
                return author.email
        return None
    
    @property
    def company_affiliations(self) -> Set[str]:
        """Return unique company affiliations."""
        result = set()
        for author in self.non_academic_authors:
            if author.company_name:
                result.add(author.company_name)
        return result

def is_non_academic_affiliation(affiliation: str) -> Tuple[bool, Optional[str]]:
    """
    Determine if an affiliation is non-academic and extract company name.
    
    Args:
        affiliation: Author affiliation string
        
    Returns:
        Tuple of (is_non_academic, company_name)
    """
    if not affiliation:
        return False, None
    
    # Check for academic indicators first
    for indicator in ACADEMIC_INDICATORS:
        if indicator.lower() in affiliation.lower():
            return False, None
    
    # Check for company indicators
    for indicator in COMPANY_INDICATORS:
        if indicator.lower() in affiliation.lower():
            # Try to extract company name - this is a simple heuristic
            # Find words around the indicator
            affiliation_lower = affiliation.lower()
            idx = affiliation_lower.find(indicator.lower())
            if idx >= 0:
                # Get a window of text around the indicator
                start = max(0, idx - 30)
                end = min(len(affiliation), idx + len(indicator) + 30)
                window = affiliation[start:end]
                
                # Find potential company name
                company_name = re.search(r'([A-Z][A-Za-z0-9\-&]+(?: [A-Z][A-Za-z0-9\-&]+){0,5})', window)
                if company_name:
                    return True, company_name.group(1)
                return True, window.strip()
            return True, None
    
    return False, None

def extract_email(text: str) -> Optional[str]:
    """Extract email address from text if present."""
    if not text:
        return None
    
    match = EMAIL_PATTERN.search(text)
    if match:
        return match.group(0)
    return None

def search_pubmed(query: str, max_results: int = 100) -> List[str]:
    """
    Search PubMed for papers matching the query.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        List of PubMed IDs
    """
    logger.debug(f"Searching PubMed with query: {query}")
    
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "usehistory": "y"
    }
    
    try:
        response = requests.get(SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "esearchresult" not in data or "idlist" not in data["esearchresult"]:
            logger.warning("No results found or unexpected API response")
            return []
        
        pmids = data["esearchresult"]["idlist"]
        logger.debug(f"Found {len(pmids)} papers")
        return pmids
    
    except (RequestException, ValueError) as e:
        logger.error(f"Error searching PubMed: {e}")
        return []

def fetch_paper_details(pmid: str) -> Optional[Paper]:
    """
    Fetch details for a single paper from PubMed.
    
    Args:
        pmid: PubMed ID
        
    Returns:
        Paper object or None if fetch failed
    """
    logger.debug(f"Fetching details for paper ID: {pmid}")
    
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml"
    }
    
    try:
        response = requests.get(FETCH_URL, params=params)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.text)
        
        # Extract basic paper details
        article_element = root.find(".//Article")
        if article_element is None:
            logger.warning(f"No article data found for PMID {pmid}")
            return None
        
        # Extract title
        title_element = article_element.find("ArticleTitle")
        title = title_element.text if title_element is not None else "Unknown Title"
        
        # Extract publication date
        pub_date = "Unknown Date"
        pub_date_element = article_element.find(".//PubDate")
        if pub_date_element is not None:
            year = pub_date_element.find("Year")
            month = pub_date_element.find("Month")
            day = pub_date_element.find("Day")
            
            if year is not None:
                pub_date = year.text
                if month is not None:
                    pub_date = f"{month.text} {pub_date}"
                    if day is not None:
                        pub_date = f"{pub_date}, {day.text}"
        
        # Extract authors
        authors = []
        author_list = article_element.find(".//AuthorList")
        
        if author_list is not None:
            for author_elem in author_list.findall("Author"):
                # Get author name
                last_name = author_elem.find("LastName")
                fore_name = author_elem.find("ForeName")
                
                if last_name is not None and fore_name is not None:
                    name = f"{fore_name.text} {last_name.text}"
                elif last_name is not None:
                    name = last_name.text
                else:
                    name = "Unknown Author"
                
                # Get affiliation
                affiliation_text = ""
                affiliation = author_elem.find(".//Affiliation")
                if affiliation is not None and affiliation.text:
                    affiliation_text = affiliation.text
                
                # Check if corresponding author
                is_corresponding = False
                if affiliation is not None and "corresponding author" in affiliation.text.lower():
                    is_corresponding = True
                
                # Extract email if present
                email = extract_email(affiliation_text)
                
                # Check if non-academic
                is_non_academic, company_name = is_non_academic_affiliation(affiliation_text)
                
                author = PaperAuthor(
                    name=name,
                    affiliation=affiliation_text,
                    email=email,
                    is_corresponding=is_corresponding,
                    is_non_academic=is_non_academic,
                    company_name=company_name
                )
                authors.append(author)
        
        return Paper(
            pubmed_id=pmid,
            title=title,
            publication_date=pub_date,
            authors=authors
        )
    
    except (RequestException, ET.ParseError) as e:
        logger.error(f"Error fetching details for PMID {pmid}: {e}")
        return None

def fetch_papers(query: str, max_results: int = 100) -> List[Paper]:
    """
    Search PubMed and fetch detailed information for matching papers.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of Paper objects
    """
    # Search for papers matching the query
    pmids = search_pubmed(query, max_results)
    
    if not pmids:
        logger.info("No papers found matching the query")
        return []
    
    # Fetch details for each paper
    papers = []
    for pmid in pmids:
        paper = fetch_paper_details(pmid)
        if paper:
            papers.append(paper)
    
    logger.info(f"Successfully fetched details for {len(papers)} papers")
    return papers

def filter_papers_with_non_academic_authors(papers: List[Paper]) -> List[Paper]:
    """
    Filter papers to keep only those with at least one non-academic author.
    
    Args:
        papers: List of Paper objects
        
    Returns:
        Filtered list of Paper objects
    """
    filtered_papers = [paper for paper in papers if paper.has_non_academic_author]
    logger.info(f"Found {len(filtered_papers)} papers with non-academic authors")
    return filtered_papers

def papers_to_csv(papers: List[Paper], output_file: Optional[str] = None) -> str:
    """
    Convert paper data to CSV format.
    
    Args:
        papers: List of Paper objects
        output_file: Optional file path to write CSV data
        
    Returns:
        CSV data as string
    """
    # Prepare CSV data
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "PubmedID", 
        "Title", 
        "Publication Date", 
        "Non-academic Author(s)", 
        "Company Affiliation(s)", 
        "Corresponding Author Email"
    ])
    
    # Write data rows
    for paper in papers:
        non_academic_authors = ", ".join([author.name for author in paper.non_academic_authors])
        company_affiliations = ", ".join(paper.company_affiliations)
        
        writer.writerow([
            paper.pubmed_id,
            paper.title,
            paper.publication_date,
            non_academic_authors,
            company_affiliations,
            paper.corresponding_author_email or ""
        ])
    
    csv_data = output.getvalue()
    
    # Write to file if specified
    if output_file:
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_data)
            logger.info(f"Results saved to {output_file}")
        except IOError as e:
            logger.error(f"Error writing to file {output_file}: {e}")
    
    return csv_data

def get_papers_by_query(query: str, output_file: Optional[str] = None, debug: bool = False) -> str:
    """
    Main function to get papers by query and output results.
    
    Args:
        query: PubMed search query
        output_file: Optional file path to save results
        debug: Whether to enable debug logging
        
    Returns:
        CSV data as string
    """
    # Set logging level based on debug flag
    if debug:
        logger.setLevel(logging.DEBUG)
    
    # Fetch and process papers
    papers = fetch_papers(query)
    filtered_papers = filter_papers_with_non_academic_authors(papers)
    
    # Generate CSV
    return papers_to_csv(filtered_papers, output_file)