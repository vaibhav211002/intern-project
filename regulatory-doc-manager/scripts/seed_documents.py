#!/usr/bin/env python3
"""
Download 6 publicly available regulatory PDFs and upload them via the API.
Run after the backend is started:  python scripts/seed_documents.py
"""
import requests
import sys
import time
import os

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

DOCUMENTS = [
    {
        "url": "https://www.ich.org/fileadmin/Public_Web_Site/ICH_Products/Guidelines/Quality/Q1A/Step4/Q1AR2_Guideline.pdf",
        "title": "ICH Q1A(R2): Stability Testing of New Drug Substances and Products",
        "tags": "ich,quality,stability",
        "filename": "ICH_Q1AR2.pdf",
    },
    {
        "url": "https://www.ich.org/fileadmin/Public_Web_Site/ICH_Products/Guidelines/Quality/Q8_R1/Step4/Q8_R2_Guideline.pdf",
        "title": "ICH Q8(R2): Pharmaceutical Development",
        "tags": "ich,quality,pharmaceutical-development",
        "filename": "ICH_Q8R2.pdf",
    },
    {
        "url": "https://www.ich.org/fileadmin/Public_Web_Site/ICH_Products/Guidelines/Safety/S1C_R2/Step4/S1C_R2__Guideline.pdf",
        "title": "ICH S1C(R2): Dose Selection for Carcinogenicity Studies",
        "tags": "ich,safety,carcinogenicity",
        "filename": "ICH_S1C_R2.pdf",
    },
    {
        "url": "https://www.ich.org/fileadmin/Public_Web_Site/ICH_Products/Guidelines/Efficacy/E6_R2/Step4/ICH_E6-R2_Step_4_2016_1109.pdf",
        "title": "ICH E6(R2): Good Clinical Practice",
        "tags": "ich,efficacy,gcp,clinical-trials",
        "filename": "ICH_E6_R2.pdf",
    },
    {
        "url": "https://www.ema.europa.eu/en/documents/scientific-guideline/ich-e2a-clinical-safety-data-management-definitions-and-standards-expedited-reporting-step-5_en.pdf",
        "title": "ICH E2A: Clinical Safety Data Management — Expedited Reporting",
        "tags": "ich,ema,safety,pharmacovigilance",
        "filename": "ICH_E2A.pdf",
    },
    {
        "url": "https://www.ema.europa.eu/en/documents/scientific-guideline/ich-q9-quality-risk-management-step-5_en.pdf",
        "title": "ICH Q9: Quality Risk Management",
        "tags": "ich,ema,quality,risk-management",
        "filename": "ICH_Q9.pdf",
    },
]

# Fallback minimal PDF if downloads fail (base64-encoded tiny valid PDF)
FALLBACK_PDF_B64 = (
    "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5k"
    "b2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPJ4K"
    "ZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3gg"
    "WzAgMCA2MTIgNzkyXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmCjAw"
    "MDAwMDAwMDkgMDAwMDAgbgowMDAwMDAwMDY4IDAwMDAwIG4KMDAwMDAwMDEyNSAwMDAwMCBu"
    "CnRyYWlsZXIKPDwKL1NpemUgNAovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKMjAzCiUlRU9G"
)


def wait_for_api(retries=15, delay=2):
    print(f"Waiting for API at {API_BASE}…", end="", flush=True)
    for _ in range(retries):
        try:
            r = requests.get(f"{API_BASE}/health", timeout=3)
            if r.ok:
                print(" ready.")
                return True
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(delay)
    print(" timed out.")
    return False


def download_pdf(url: str) -> bytes | None:
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        if r.ok and r.headers.get("content-type", "").startswith("application/pdf"):
            return r.content
        print(f"  [warn] unexpected response ({r.status_code}) from {url}")
    except Exception as e:
        print(f"  [warn] download failed: {e}")
    return None


def upload(title, filename, pdf_bytes, tags):
    r = requests.post(
        f"{API_BASE}/documents/upload",
        files={"file": (filename, pdf_bytes, "application/pdf")},
        data={"title": title, "tags": tags},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def main():
    if not wait_for_api():
        sys.exit(1)

    import base64

    fallback = base64.b64decode(FALLBACK_PDF_B64)

    for doc in DOCUMENTS:
        print(f"\nProcessing: {doc['title'][:60]}…")
        pdf_bytes = download_pdf(doc["url"])
        if pdf_bytes is None:
            print("  Using minimal fallback PDF (text extraction will be empty).")
            pdf_bytes = fallback
        try:
            result = upload(doc["title"], doc["filename"], pdf_bytes, doc["tags"])
            print(f"  ✓ Uploaded — id={result['id']}, pages={result['page_count']}")
        except Exception as e:
            print(f"  ✗ Upload failed: {e}")

    print("\nSeeding complete.")


if __name__ == "__main__":
    main()
