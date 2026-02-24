import requests
import csv

CATEGORIES = [
    "SEO",
    "Digital Marketing",
    "Marketing",
    "Social Media",
    "Website Design",
    "LinkedIn Management"
]

OUTPUT_FILE = "usa_marketing_jobs.csv"

all_jobs = []

# =============================
# 1️⃣ REMOTEOK (API)
# =============================
print("Scraping RemoteOK...")

headers = {"User-Agent": "Mozilla/5.0"}

remote_data = requests.get("https://remoteok.com/api", headers=headers).json()

for category in CATEGORIES:
    for job in remote_data[1:]:  # skip metadata
        title = job.get("position", "")
        if category.lower() in title.lower():
            all_jobs.append({
                "source": "RemoteOK",
                "category": category,
                "title": title,
                "company": job.get("company"),
                "location": job.get("location"),
                "url": f"https://remoteok.com{job.get('url')}"
            })

# =============================
# 2️⃣ USAJOBS (OFFICIAL API)
# =============================
print("Scraping USAJobs...")

API_KEY = "375e5fd4-e3bd-454d-bd76-207738314c45"
USER_EMAIL = "daniel.dimitar.lee@gmail.com"

headers = {
    "Host": "data.usajobs.gov",
    "User-Agent": USER_EMAIL,
    "Authorization-Key": API_KEY
}

for category in CATEGORIES:
    params = {
        "Keyword": category,
        "LocationName": "United States",
        "ResultsPerPage": 50
    }

    response = requests.get(
        "https://data.usajobs.gov/api/search",
        headers=headers,
        params=params
    )

    data = response.json()

    for item in data.get("SearchResult", {}).get("SearchResultItems", []):
        job = item["MatchedObjectDescriptor"]

        all_jobs.append({
            "source": "USAJobs",
            "category": category,
            "title": job.get("PositionTitle"),
            "company": job.get("OrganizationName"),
            "location": job.get("PositionLocationDisplay"),
            "url": job.get("PositionURI")
        })

# =============================
# SAVE CSV
# =============================
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["source","category","title","company","location","url"]
    )
    writer.writeheader()
    writer.writerows(all_jobs)

print(f"Saved {len(all_jobs)} jobs to {OUTPUT_FILE}")