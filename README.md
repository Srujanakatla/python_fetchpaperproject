# PubMed Papers Fetcher

A Python tool to fetch research papers from PubMed and identify those with authors affiliated with pharmaceutical or biotech companies.

## 🔍 Overview

This tool searches PubMed for papers matching a user-specified query, identifies papers with at least one author affiliated with a pharmaceutical or biotech company, and outputs the results in CSV format. It's designed for researchers and analysts who need to track industry involvement in academic publishing.

## 🚀 Features

- Search PubMed using full query syntax
- Identify papers with pharmaceutical/biotech company affiliations
- Extract corresponding author email addresses
- Export results to CSV
- Command-line interface with debug options

## 📋 Requirements

- Python 3.8+
- `requests` library

## 🛠️ Installation

### Option 1: Using pip (from TestPyPI)

```bash
pip install -i https://test.pypi.org/simple/ pubmed-papers-fetcher
```

### Option 2: Manual installation

1. Clone the repository:
```bash
git clone https://github.com/Srujanakatla/python_fetchpaperproject
cd pubmed-papers-fetcher
```

2. Install dependencies:
```bash
pip install requests
```

OR if you're using Poetry:
```bash
poetry install
```

## 🖥️ Usage

### Basic Usage

```bash
# If installed via pip or Poetry
get-papers-list "cancer immunotherapy"

# If running from the cloned repository
python pubmed_cli.py "cancer immunotherapy"
```

### Command-line Options

```
usage: get-papers-list [-h] [-f FILE] [-d] query

Fetch research papers from PubMed with pharmaceutical/biotech company affiliations

positional arguments:
  query                 PubMed search query

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  File to save results (if not provided, prints to console)
  -d, --debug           Enable debug output
```

### Examples

Search for COVID-19 vaccine papers and save results to a file:
```bash
python pubmed_cli.py "COVID-19 vaccine" --file covid_papers.csv
```

Search for Alzheimer's disease papers with debug information:
```bash
python pubmed_cli.py "Alzheimer's disease treatment" --debug
```

## 📊 Output Format

The tool produces a CSV with the following columns:

1. **PubmedID**: Unique identifier for the paper
2. **Title**: Title of the paper
3. **Publication Date**: Date the paper was published
4. **Non-academic Author(s)**: Names of authors affiliated with non-academic institutions
5. **Company Affiliation(s)**: Names of pharmaceutical/biotech companies
6. **Corresponding Author Email**: Email address of the corresponding author

## 📂 Project Structure

```
pubmed-papers-fetcher/
├── pubmed_papers_fetcher.py  # Main module with core functionality
├── pubmed_cli.py             # Command-line interface
├── pyproject.toml            # Poetry configuration (if using Poetry)
└── README.md                 # This documentation
```

## 🧠 How It Works

1. **Search**: The tool sends a search query to PubMed's E-utilities API
2. **Fetch**: For each search result, it fetches detailed paper information
3. **Analyze**: Author affiliations are analyzed using pattern matching to identify company associations
4. **Filter**: Papers are filtered to include only those with at least one industry-affiliated author
5. **Output**: Results are formatted as CSV and either displayed or saved to a file

## 🔧 Development

### Publishing to TestPyPI

If using Poetry:
```bash
poetry build
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish -r testpypi
```

## 🔌 Tools and Libraries Used

- [Python](https://www.python.org/) - Programming language
- [Requests](https://requests.readthedocs.io/) - HTTP library for API calls
- [Poetry](https://python-poetry.org/) (optional) - Dependency management
- [PubMed E-utilities API](https://www.ncbi.nlm.nih.gov/books/NBK25500/) - Data source
- [GitHub](https://github.com/) - Version control and hosting

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
