# PubMed Papers Fetcher

A command-line tool to fetch research papers from PubMed based on a user-specified query, identifying papers with at least one author affiliated with a pharmaceutical or biotech company.

## Code Organization

The project is organized into two main components:

1. **Module (`pubmed_papers_fetcher.py`)**: Contains the core functionality for:
   - Searching PubMed for papers
   - Fetching paper details
   - Identifying non-academic authors
   - Converting results to CSV format

2. **Command-line Interface (`pubmed_cli.py`)**: Provides a user-friendly command-line interface to the module.

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pubmed-papers-fetcher.git
   cd pubmed-papers-fetcher
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

This will set up all required dependencies and make the `get-papers-list` command available in your environment.

## Usage

### Basic Usage

```bash
get-papers-list "cancer immunotherapy"
```

This will search for papers related to cancer immunotherapy, identify those with authors from pharmaceutical/biotech companies, and print the results to the console.

### Command-line Options

- `query`: PubMed search query (required positional argument)
- `-f, --file`: Specify a filename to save the results as CSV
- `-d, --debug`: Enable debug output for troubleshooting
- `-h, --help`: Display usage instructions

### Examples

Search for COVID-19 vaccine papers and save results to a file:
```bash
get-papers-list "COVID-19 vaccine" --file covid_papers.csv
```

Search for Alzheimer's disease papers with debug information:
```bash
get-papers-list "Alzheimer's disease treatment" --debug
```

## Output Format

The tool produces a CSV with the following columns:

1. **PubmedID**: Unique identifier for the paper
2. **Title**: Title of the paper
3. **Publication Date**: Date the paper was published
4. **Non-academic Author(s)**: Names of authors affiliated with non-academic institutions
5. **Company Affiliation(s)**: Names of pharmaceutical/biotech companies
6. **Corresponding Author Email**: Email address of the corresponding author

## How It Works

The tool works by:
1. Searching PubMed using the provided query
2. Fetching detailed information for each paper
3. Analyzing author affiliations to identify non-academic authors
4. Filtering papers to include only those with at least one non-academic author
5. Generating a CSV output with the relevant information

## Testing PyPI Publication

This module is also available on Test PyPI. You can install it using:

```bash
pip install -i https://test.pypi.org/simple/ pubmed-papers-fetcher
```

## Tools and Libraries Used

This project was built using:

- [Python](https://www.python.org/) - Programming language
- [Poetry](https://python-poetry.org/) - Dependency management and packaging
- [Requests](https://requests.readthedocs.io/) - HTTP library for API calls
- [argparse](https://docs.python.org/3/library/argparse.html) - Command-line argument parsing
- [PubMed E-utilities API](https://www.ncbi.nlm.nih.gov/books/NBK25500/) - For fetching paper data

## Development

### Publishing to Test PyPI

```bash
poetry build
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish -r testpypi
```

### Running Tests

```bash
poetry run pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.