import logging
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import date, timedelta, datetime, timezone
from typing import List, Dict, Optional, Any

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# RSS feed URLs
RSS_FEEDS = {
    'cs': 'https://rss.arxiv.org/rss/cs',
    'q-fin': 'https://rss.arxiv.org/rss/q-fin',
}

# Target subcategories to filter
TARGET_CATEGORIES = {'q-fin.PM', 'q-fin.TR', 'cs.LG', 'cs.AI', 'cs.CL'}

# XML namespaces
NAMESPACES = {
    'arxiv': 'http://arxiv.org/schemas/atom',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'atom': 'http://www.w3.org/2005/Atom',
}


def _parse_rss_item(item: ET.Element) -> Optional[Dict[str, Any]]:
    """Parse a single RSS <item> element into a paper dict."""
    title = item.findtext('title', '').strip()
    url = item.findtext('link', '').strip()
    description = item.findtext('description', '').strip()

    # Extract abstract from description: "arXiv:ID Announce Type: ...\nAbstract: ..."
    summary = ''
    abstract_marker = 'Abstract: '
    if abstract_marker in description:
        summary = description.split(abstract_marker, 1)[1].strip()
    # Collapse whitespace in abstract (newlines, multiple spaces)
    import re
    summary = re.sub(r'\s+', ' ', summary)

    # Categories: can have multiple <category> elements
    categories = [cat.text.strip() for cat in item.findall('category') if cat.text]

    # Published date
    pub_date_str = item.findtext('pubDate', '').strip()
    published_date = None
    if pub_date_str:
        try:
            published_date = parsedate_to_datetime(pub_date_str)
        except Exception:
            pass

    # Authors from dc:creator
    authors_str = item.findtext('dc:creator', '', NAMESPACES).strip()
    authors = [a.strip() for a in authors_str.split(',') if a.strip()] if authors_str else []

    return {
        'title': title,
        'summary': summary,
        'url': url,
        'published_date': published_date,
        'updated_date': published_date,  # RSS doesn't distinguish
        'categories': categories,
        'authors': authors,
    }


def fetch_papers_via_rss(target_categories: Optional[set] = None) -> List[Dict[str, Any]]:
    """Fetch today's papers from arXiv RSS feeds.

    Fetches from cs and q-fin RSS feeds, filters by target subcategories,
    deduplicates, and returns papers in the same format as fetch_cv_papers.

    Args:
        target_categories: Set of category strings to filter (e.g. {'cs.AI', 'q-fin.TR'}).
                          Defaults to TARGET_CATEGORIES if None.

    Returns:
        List of paper dicts with keys: title, summary, url, published_date,
        updated_date, categories, authors.
    """
    if target_categories is None:
        target_categories = TARGET_CATEGORIES

    seen_urls = set()
    papers = []

    for feed_name, feed_url in RSS_FEEDS.items():
        logging.info(f"Fetching RSS feed: {feed_url}")
        try:
            resp = requests.get(feed_url, timeout=60)
            resp.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Failed to fetch RSS feed {feed_url}: {e}")
            continue

        try:
            root = ET.fromstring(resp.content)
        except ET.ParseError as e:
            logging.error(f"Failed to parse RSS XML from {feed_url}: {e}")
            continue

        channel = root.find('channel')
        if channel is None:
            logging.warning(f"No <channel> found in RSS feed {feed_url}")
            continue

        items = channel.findall('item')
        logging.info(f"Found {len(items)} items in {feed_name} RSS feed")

        for item in items:
            paper = _parse_rss_item(item)
            if paper is None or not paper['url']:
                continue

            # Deduplicate by URL
            if paper['url'] in seen_urls:
                continue
            seen_urls.add(paper['url'])

            # Filter by target categories (paper must have at least one matching category)
            if not target_categories:
                # No filter, keep all
                papers.append(paper)
            elif any(cat in target_categories for cat in paper['categories']):
                papers.append(paper)

    logging.info(f"Total papers after filtering and deduplication: {len(papers)}")
    return papers


# --- Legacy API-based fetcher (fallback for historical dates) ---

import arxiv  # Only needed for the legacy API-based fetcher

def fetch_cv_papers(category: str = 'q-fin.PM OR q-fin.TR OR cs.LG OR cs.AI OR cs.CL', max_results: int = 500, specified_date: Optional[date] = None) -> List[Dict[str, Any]]:
    """Fetches quantitative finance and AI papers from arXiv for a given date.

    Fetches papers from categories including q-fin.PM (Portfolio Management),
    q-fin.TR (Trading), cs.LG (Learning), cs.AI (Artificial Intelligence),
    and cs.CL (Computation and Language).

    Args:
        category (str): The arXiv categories combined with OR logic (e.g., 'q-fin.PM OR q-fin.TR OR cs.LG OR cs.AI OR cs.CL').
        max_results (int): The maximum number of results to retrieve.
        specified_date (Optional[date]): The specific date to fetch papers for (UTC).
                                         Defaults to today UTC date.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary contains
                              the 'title', 'summary', 'url', 'published_date',
                              'updated_date', 'categories', and 'authors' of a paper.
                              Returns an empty list if an error occurs or no papers are found.
    """
    if specified_date is None:
        # Default to today (UTC)
        specified_date = datetime.now(timezone.utc).date()
        logging.info(f"No date specified, defaulting to {specified_date.strftime('%Y-%m-%d')} UTC.")
    else:
        logging.info(f"Fetching papers for specified date: {specified_date.strftime('%Y-%m-%d')} UTC.")
    
    # 将specified_date转为datetime
    specified_date = datetime.combine(specified_date, datetime.min.time())
    specified_date = specified_date - timedelta(hours=6) # 转换到arxiv时区

    # Format for arXiv API: YYYYMMDDHHMM
    start_time = specified_date - timedelta(days=1)
    start_time_str = start_time.strftime('%Y%m%d%H%M')
    end_time_str = specified_date.strftime('%Y%m%d%H%M')

    # Construct the search query for multiple categories with OR logic
    # Parse category if it contains ' OR ', otherwise treat as single category
    if ' OR ' in category:
        # Category is already formatted with OR logic
        categories = category
    else:
        # Single category
        categories = f'cat:{category}'

    query = f'({categories}) AND submittedDate:[{start_time_str} TO {end_time_str}]'
    logging.info(f"Using arXiv query: {query}")

    # Create client with increased delay to avoid rate limiting
    # arXiv API allows 1 request per 3 seconds, we set 5 seconds to be safe
    client = arxiv.Client(
        page_size=100,
        delay_seconds=5.0,
        num_retries=5
    )
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    papers: List[Dict[str, Any]] = []
    try:
        results = client.results(search)
        # Iterate through the generator
        count = 0
        for result in results:
            papers.append({
                'title': result.title,
                'summary': result.summary.strip(),
                'url': result.entry_id,
                'published_date': result.published,
                'updated_date': result.updated,
                'categories': result.categories,
                'authors': [author.name for author in result.authors],
            })
            count += 1
        logging.info(f"Successfully fetched {count} papers submitted on {specified_date.strftime('%Y-%m-%d')} from {category}.")

    except arxiv.UnexpectedEmptyPageError as e:
        logging.warning(f"arXiv query returned an empty page (potentially no results for the date/query): {e}")
        # This might not be a critical error, could just mean no papers found
    except arxiv.HTTPError as e:
        status_code = getattr(e, 'status_code', None)
        if status_code == 429:
            logging.error(f"arXiv API rate limit exceeded (HTTP 429). Please increase the delay between requests or reduce the number of consecutive requests.")
        else:
            logging.error(f"HTTP error during arXiv search (status {status_code}): {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during arXiv search: {e}", exc_info=True)
        # Log the full traceback for unexpected errors

    return papers

if __name__ == '__main__':
    logging.info("Testing RSS-based arXiv paper fetching...")
    papers = fetch_papers_via_rss()

    if papers:
        logging.info(f"--- Found {len(papers)} Papers via RSS ---")
        for i, paper in enumerate(papers):
            print(f"{i+1}. {paper['title']} [{', '.join(paper['categories'])}]")
    else:
        print("No papers found via RSS or an error occurred.")