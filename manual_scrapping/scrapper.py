import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://itjobpro.com"
JOBS_PAGE = f"{BASE_URL}/jobs/"
AJAX_URL = f"{BASE_URL}/jm-ajax/get_listings/"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
}

session = requests.Session()
session.headers.update(HEADERS)


def get_tokens():
    """Extract hidden CSRF tokens from jobs page"""
    r = session.get(JOBS_PAGE)
    soup = BeautifulSoup(r.text, "html.parser")

    tokens = {}
    hidden_inputs = soup.select("input[type='hidden']")

    for inp in hidden_inputs:
        name = inp.get("name")
        value = inp.get("value")
        if name and value:
            tokens[name] = value

    return tokens


def fetch_page(page, tokens):
    payload = {
        "search_keywords": "",
        "search_location": "",
        "per_page": 10,
        "page": page,
        "orderby": "featured",
        "order": "DESC",
    }

    payload.update(tokens)

    r = session.post(AJAX_URL, data=payload)

    if r.status_code != 200:
        print(f"Error on page {page}")
        return []

    data = r.json()
    html_fragment = data.get("html", "")

    if not html_fragment.strip():
        return []

    soup = BeautifulSoup(html_fragment, "html.parser")
    job_items = soup.select("li.list-item")

    jobs = []

    for job in job_items:
        title_tag = job.select_one(".list-item-title a")
        title = title_tag.get_text(strip=True) if title_tag else ""
        url = title_tag["href"] if title_tag else ""

        company_tag = job.select_one(".list-item-company")
        company = company_tag.get_text(strip=True) if company_tag else ""

        location_tag = job.select_one(".list-item-location")
        location = location_tag.get_text(strip=True) if location_tag else ""

        time_tag = job.select_one(".list-item-time")
        posted = time_tag.get_text(strip=True) if time_tag else ""

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "posted": posted,
            "url": url
        })

    return jobs


def scrape_all_jobs():
    tokens = get_tokens()
    all_jobs = []
    page = 1

    while True:
        print(f"Fetching page {page}...")
        jobs = fetch_page(page, tokens)

        if not jobs:
            print("No more jobs found. Stopping.")
            break

        all_jobs.extend(jobs)
        print(f"Collected {len(jobs)} jobs from page {page}")

        page += 1
        time.sleep(1)  # polite delay

    return all_jobs


def save_to_csv(jobs, filename="itjobpro_jobs.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["title", "company", "location", "posted", "url"]
        )
        writer.writeheader()
        writer.writerows(jobs)


if __name__ == "__main__":
    jobs = scrape_all_jobs()
    print(f"\nTotal jobs scraped: {len(jobs)}")

    save_to_csv(jobs)
    print("Saved to itjobpro_jobs.csv")