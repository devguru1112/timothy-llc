import requests
from bs4 import BeautifulSoup
import sqlite3
import csv
import time
from datetime import datetime

BASE_URL = "https://itjobpro.com"
JOBS_PAGE = f"{BASE_URL}/jobs/"
AJAX_URL = f"{BASE_URL}/jm-ajax/get_listings/"

KEYWORDS = [
    "SEO",
    "Marketing",
    "Social Media",
    "Website Design",
    "LinkedIn Management"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
}

session = requests.Session()
session.headers.update(HEADERS)


# -------------------------
# DATABASE SETUP
# -------------------------
conn = sqlite3.connect("itjobpro_jobs.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    url TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    posted TEXT,
    job_type TEXT,
    salary TEXT,
    description TEXT,
    category TEXT,
    scraped_at TEXT
)
""")

conn.commit()


# -------------------------
# TOKEN EXTRACTION
# -------------------------
def get_tokens():
    r = session.get(JOBS_PAGE)
    soup = BeautifulSoup(r.text, "html.parser")

    tokens = {}
    for inp in soup.select("input[type='hidden']"):
        name = inp.get("name")
        value = inp.get("value")
        if name and value:
            tokens[name] = value

    return tokens


# -------------------------
# FETCH AJAX LISTINGS
# -------------------------
def fetch_page(keyword, page, tokens):
    payload = {
        "search_keywords": keyword,
        "search_location": "",
        "per_page": 10,
        "page": page,
        "orderby": "date",
        "order": "DESC",
    }

    payload.update(tokens)

    r = session.post(AJAX_URL, data=payload)
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

        company = job.select_one(".list-item-company")
        location = job.select_one(".list-item-location")
        posted = job.select_one(".list-item-time")

        jobs.append({
            "title": title,
            "url": url,
            "company": company.get_text(strip=True) if company else "",
            "location": location.get_text(strip=True) if location else "",
            "posted": posted.get_text(strip=True) if posted else "",
            "category": keyword
        })

    return jobs


# -------------------------
# SCRAPE FULL JOB PAGE
# -------------------------
def scrape_job_detail(job):
    r = session.get(job["url"])
    soup = BeautifulSoup(r.text, "html.parser")

    description = ""
    desc_container = soup.select_one(".job-description")
    if desc_container:
        description = desc_container.get_text("\n", strip=True)

    salary = ""
    salary_tag = soup.find(string=lambda t: "salary" in t.lower() if t else False)
    if salary_tag:
        salary = salary_tag.strip()

    job_type = ""
    job_type_tag = soup.find(string=lambda t: "Full Time" in t or "Part Time" in t if t else False)
    if job_type_tag:
        job_type = job_type_tag.strip()

    job["description"] = description
    job["salary"] = salary
    job["job_type"] = job_type

    return job


# -------------------------
# SAVE TO DATABASE
# -------------------------
def save_job(job):
    try:
        cursor.execute("""
        INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job["url"],
            job["title"],
            job["company"],
            job["location"],
            job["posted"],
            job.get("job_type", ""),
            job.get("salary", ""),
            job.get("description", ""),
            job["category"],
            datetime.now().isoformat()
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


# -------------------------
# SCRAPE EVERYTHING
# -------------------------
def scrape_all():
    tokens = get_tokens()
    new_jobs = []

    for keyword in KEYWORDS:
        print(f"\nScraping keyword: {keyword}")
        page = 1

        while True:
            jobs = fetch_page(keyword, page, tokens)
            if not jobs:
                break

            for job in jobs:
                job = scrape_job_detail(job)
                is_new = save_job(job)
                if is_new:
                    new_jobs.append(job)

            page += 1
            time.sleep(1)

    return new_jobs


# -------------------------
# EXPORT CSV
# -------------------------
def export_csv():
    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()

    with open("itjobpro_jobs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "url","title","company","location","posted",
            "job_type","salary","description","category","scraped_at"
        ])
        writer.writerows(rows)


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    new_jobs = scrape_all()
    print(f"\nNew jobs added today: {len(new_jobs)}")

    export_csv()
    print("CSV exported: itjobpro_jobs.csv")

    conn.close()