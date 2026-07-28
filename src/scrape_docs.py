import requests
import trafilatura
import time
import os

# List of Razorpay documentation page URLs to scrape
URLS = [
    # Payments
    "https://razorpay.com/docs/payments/payments/apis/",
    "https://razorpay.com/docs/payments/payments/faqs/",
    "https://razorpay.com/docs/payments/payments/test-card-details/",
    "https://razorpay.com/docs/payments/payments/capture-settings/",
    "https://razorpay.com/docs/payments/payments/dashboard/",

    # Payment Links
    "https://razorpay.com/docs/payments/payment-links/apis/",

    # Settlements
    "https://razorpay.com/docs/payments/settlements/",
    "https://razorpay.com/docs/payments/settlements/dashboard/",

    # Refunds
    "https://razorpay.com/docs/api/refunds/",
    "https://razorpay.com/docs/payments/refunds/view/",
    "https://razorpay.com/docs/payments/refunds/subscribe-to-webhooks/",

    # Disputes
    "https://razorpay.com/docs/payments/disputes/",
    "https://razorpay.com/docs/api/disputes/",
    "https://razorpay.com/docs/api/disputes/accept/",

    # Webhooks
    "https://razorpay.com/docs/webhooks/",
    "https://razorpay.com/docs/api/partners/webhooks/",
    "https://razorpay.com/docs/webhooks/refunds/",

    # Route (split payments)
    "https://razorpay.com/docs/api/route/",
    "https://razorpay.com/docs/route/operations/",

    # Web integration
    "https://razorpay.com/docs/payments/payment-gateway/web-integration/standard/integration-steps/",
]

# Where to save the scraped text files
OUTPUT_DIR = "data/raw"

# Make sure the output folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def scrape_page(url):
    """
    Downloads a webpage and extracts clean article text.
    Returns the extracted text, or None if it failed.
    """
    try:
        downloaded = trafilatura.fetch_url(url)

        if downloaded is None:
            print(f"Failed to download: {url}")
            return None

        text = trafilatura.extract(downloaded)
        return text
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def url_to_filename(url):
    """
    Converts a URL into a safe filename.
    """
    path = url.replace("https://razorpay.com/docs/", "")
    path = path.rstrip("/")
    filename = path.replace("/", "_") + ".txt"
    return filename

# Main loop: go through each URL, scrape it, save it
for url in URLS:
    print(f"Scraping: {url}")

    text = scrape_page(url)

    if text:
        filename = url_to_filename(url)
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"  Saved to: {filepath} ({len(text)} characters)")
    else:
        print(f"  Skipped (no content extracted)")

    time.sleep(2)

print("\nDone! Check the data/raw folder.")