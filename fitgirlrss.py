#!/usr/bin/python3
import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import time
import sys
import html

FEED_URL = "https://fitgirl-repacks.site/feed/"
JSON_FILE = "/var/local/fitgirlrss.json"

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("CRITICAL: Missing Telegram environment variables!", file=sys.stderr, flush=True)
    sys.exit(1)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"  [Telegram Error] Failed to send message: {e}", file=sys.stderr, flush=True)
        return None

def fetch_feed():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        req = urllib.request.Request(FEED_URL, headers=headers)
        
        print("Connecting to FitGirl RSS feed...", flush=True)
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
            
        print(f"Successfully fetched {len(xml_data)} bytes of feed data.", flush=True)
        root = ET.fromstring(xml_data)
        items = []
        for item in root.findall(".//item"):
            title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            guid = item.find("guid").text if item.find("guid") is not None else link
            items.append({"title": title, "link": link, "guid": guid})
        return items
    except Exception as e:
        print(f"  [Feed Error] Cloudflare or network blocked request: {e}", file=sys.stderr, flush=True)
        return []

def main():
    os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
    
    # Initialize tracking variables
    is_absolute_first_run = not os.path.exists(JSON_FILE)
    print("System active. Entering monitoring loop...", flush=True)

    while True:
        # Reload the database from disk dynamically at the start of every single loop
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r") as f:
                    seen = set(json.load(f))
            except Exception as e:
                print(f"Database parse warning (JSON might be malformed): {e}. Treating as empty.", flush=True)
                seen = set()
        else:
            seen = set()

        items = fetch_feed()
        new_items = []
        
        for item in reversed(items):
            if item["guid"] not in seen:
                seen.add(item["guid"])
                new_items.append(item)
                
        if new_items:
            print(f"Found {len(new_items)} untracked items. Processing...", flush=True)
            try:
                with open(JSON_FILE, "w") as f:
                    json.dump(list(seen), f)
            except Exception as e:
                print(f"  [Database Error] Could not save update to JSON: {e}", file=sys.stderr, flush=True)
                
            for item in new_items:
                safe_title = html.escape(item['title'])
                print(f"Sending notification for: {item['title']}", flush=True)
                
                # If the JSON file was completely empty at script boot, treat as quiet historical dump
                if is_absolute_first_run:
                    msg = f"<b>{safe_title}</b>\n{item['link']}"
                    send_telegram(msg)
                    time.sleep(1.5)
                else:
                    # If user manually deleted a single game from the JSON, it triggers explicitly as new alert
                    msg = f"<b>New Release Arrived:</b>\n{safe_title}\n{item['link']}"
                    send_telegram(msg)
                    time.sleep(1.5)
        else:
            print("No new releases found on this check.", flush=True)
                    
        is_absolute_first_run = False
        print("Sleeping for 5 seconds before next check...\n", flush=True)
        time.sleep(5)

if __name__ == "__main__":
    main()