#!/usr/bin/env python
"""
Command-line tool to fetch research papers from PubMed with pharmaceutical/biotech company affiliations.
"""

import argparse
import sys
import logging
from typing import List, Optional

from pubmed_papers_fetcher import get_papers_by_query, logger

def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Fetch research papers from PubMed with pharmaceutical/biotech company affiliations",
        prog="get-papers-list"
    )
    
    parser.add_argument(
        "query",
        help="PubMed search query"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="File to save results (if not provided, prints to console)",
        default=None
    )
    
    parser.add_argument(
        "-d", "--debug",
        help="Enable debug output",
        action="store_true"
    )
    
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the command-line tool.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Parse arguments
        parsed_args = parse_arguments(args)
        
        # Configure logging based on debug flag
        if parsed_args.debug:
            logger.setLevel(logging.DEBUG)
        
        # Process the query
        csv_data = get_papers_by_query(
            query=parsed_args.query,
            output_file=parsed_args.file,
            debug=parsed_args.debug
        )
        
        # If no output file specified, print to console
        if not parsed_args.file:
            print(csv_data)
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())