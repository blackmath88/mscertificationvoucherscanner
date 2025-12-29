import json, requests, hashlib, os, re
from bs4 import BeautifulSoup

STATE_DIR = "state"
os.makedirs(STATE_DIR, exist_ok=True)

KEYWORD_REGEX = re.compile(
    r"(voucher|free exam|100%|50% off|exam discount|skills challenge|redeem)", 
    re.IGNORECASE
)


def get_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

with open("sources.json", "r") as f:
    sources = json.load(f)

alerts = []

for src in sources:
    print(f"Checking {src['name']} …")

    try:
        resp = requests.get(src["url"], timeout=15)
        resp.raise_for_status()
        content = resp.text
    except Exception as e:
        print(f" ⚠ failed to fetch {src['name']}: {e}")
        continue

    page_hash = get_hash(content)
    state_file = f"{STATE_DIR}/{src['id']}.hash"

    old_hash = None
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            old_hash = f.read()

    # If updated
    if old_hash != page_hash:
        print(f" 🔄 Change detected for {src['name']}")
        with open(state_file, "w") as f:
            f.write(page_hash)

        # keyword scan
        if KEYWORD_REGEX.search(content):
            alerts.append(f"{src['name']} has potential voucher/offer content: {src['url']}")
        else:
            print("   → No keywords found.")

print("\nDone scanning.\n")

if alerts:
    print("POTENTIAL ALERTS:")
    for a in alerts:
        print(" *", a)
else:
    print("No alerts.")
