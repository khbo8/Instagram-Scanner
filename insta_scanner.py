import requests
import random
import string
import json
import os
import sys
import time

# ------------- Configuration -------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
MIN_LEN = 5
MAX_LEN = 9
# -----------------------------------------

def log(msg):
    print(f"[LOG] {msg}", flush=True)

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        log("❌ TELEGRAM SECRETS NOT SET! Check BOT_TOKEN and CHAT_ID in GitHub Secrets.")
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=15)
        if r.status_code == 200:
            log("✅ Telegram message sent successfully")
            return True
        else:
            log(f"❌ Telegram API error: {r.status_code} - {r.text[:200]}")
            return False
    except Exception as e:
        log(f"❌ Telegram send exception: {e}")
        return False

def generate_username():
    patterns = [
        lambda: random.choice(["the", "im", "its", "mr", "ms", "itz"]) + random.choice(string.ascii_lowercase) + ''.join(random.choices(string.ascii_lowercase, k=random.randint(3,6))),
        lambda: ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 8))) + str(random.randint(1, 999)),
        lambda: random.choice(["x", "z", "v"]) + ''.join(random.choices(string.ascii_lowercase, k=random.randint(4,7))) + str(random.randint(10, 99)),
        lambda: ''.join(random.choices(string.ascii_lowercase, k=random.randint(6, 9))) + random.choice(["_", "", ""]) + random.choice(["official", "real", "king", "lol", "pro", ""]),
    ]
    return random.choice(patterns)()

def check_instagram(username):
    """Try multiple methods to get Instagram account info"""
    # Method 1: Public API (www.instagram.com/{username}/?__a=1)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/html, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.instagram.com/",
    }
    
    # Method A: __a=1 API
    try:
        url = f"https://www.instagram.com/{username}/?__a=1"
        r = requests.get(url, headers=headers, timeout=10)
        log(f"  Method A ({username}): Status {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            user_data = data.get("graphql", {}).get("user", {}) or data.get("user", {})
            if user_data and user_data.get("username", "").lower() == username.lower():
                return {
                    "username": user_data.get("username"),
                    "full_name": user_data.get("full_name"),
                    "bio": user_data.get("biography", ""),
                    "email": user_data.get("business_email") or user_data.get("contact_phone_number", "") or "N/A",
                    "followers": user_data.get("edge_followed_by", {}).get("count", 0),
                    "following": user_data.get("edge_follow", {}).get("count", 0),
                    "is_private": user_data.get("is_private", False),
                    "is_business": user_data.get("is_business_account", False),
                    "verified": user_data.get("is_verified", False),
                    "profile_pic": user_data.get("profile_pic_url_hd", ""),
                }
    except Exception as e:
        log(f"  Method A failed: {e}")
    
    # Method B: Direct page scrape (no __a=1)
    try:
        url = f"https://www.instagram.com/{username}/"
        r = requests.get(url, headers=headers, timeout=10)
        log(f"  Method B ({username}): Status {r.status_code}, Length: {len(r.text)}")
        if r.status_code == 200 and "window.__INITIAL_STATE__" in r.text:
            import re
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});\s*\(function', r.text, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                user_data = data.get("user", {})
                if user_data:
                    return {
                        "username": user_data.get("username"),
                        "full_name": user_data.get("full_name"),
                        "bio": user_data.get("biography", ""),
                        "email": user_data.get("business_email", "N/A"),
                        "followers": user_data.get("edge_followed_by", {}).get("count", 0),
                        "following": user_data.get("edge_follow", {}).get("count", 0),
                        "is_private": user_data.get("is_private", False),
                        "is_business": user_data.get("is_business_account", False),
                        "verified": user_data.get("is_verified", False),
                        "profile_pic": "",
                    }
    except Exception as e:
        log(f"  Method B failed: {e}")
    
    return None

def main():
    log("=" * 50)
    log("INSTAGRAM RANDOM SCANNER STARTED")
    log(f"Python version: {sys.version}")
    log(f"BOT_TOKEN set: {'YES' if BOT_TOKEN else 'NO'}")
    log(f"CHAT_ID set: {'YES' if CHAT_ID else 'NO'}")
    log("=" * 50)
    
    total_checked = 0
    found_accounts = []
    
    # Send startup notification
    send_telegram("🤖 <b>Instagram Scanner Started</b>\nScanning random usernames...")
    
    max_attempts = 50  # Limit for GitHub Actions (6 min timeout)
    
    for attempt in range(1, max_attempts + 1):
        username = generate_username()
        total_checked += 1
        log(f"\n[{attempt}/{max_attempts}] Checking: {username}")
        
        try:
            result = check_instagram(username)
            
            if result:
                log(f"✅ FOUND: {username} - {result.get('full_name', 'N/A')}")
                found_accounts.append(result)
                
                # Send immediate Telegram notification
                msg = (
                    f"🎯 <b>Instagram Account Found!</b>\n\n"
                    f"👤 <b>Username:</b> @{result['username']}\n"
                    f"📛 <b>Name:</b> {result.get('full_name', 'N/A')}\n"
                    f"📧 <b>Email:</b> {result.get('email', 'N/A')}\n"
                    f"👥 <b>Followers:</b> {result.get('followers', 0):,}\n"
                    f"🔒 <b>Private:</b> {'Yes' if result.get('is_private') else 'No'}\n"
                    f"✅ <b>Verified:</b> {'Yes' if result.get('verified') else 'No'}\n"
                    f"📝 <b>Bio:</b> {result.get('bio', 'N/A')[:100]}"
                )
                send_telegram(msg)
            else:
                log(f"❌ Not found or API blocked: {username}")
        
        except Exception as e:
            log(f"⚠️ Unexpected error on {username}: {e}")
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    log("=" * 50)
    log(f"SCAN COMPLETE: Checked {total_checked} usernames")
    log(f"Found: {len(found_accounts)} accounts")
    log("=" * 50)
    
    # Save found accounts
    if found_accounts:
        with open("found_accounts.json", "w") as f:
            json.dump(found_accounts, f, indent=2)
        log(f"Saved {len(found_accounts)} accounts to found_accounts.json")
        
        summary = f"📊 <b>Scan Complete</b>\nChecked: {total_checked}\nFound: {len(found_accounts)} accounts"
        send_telegram(summary)
    else:
        log("No accounts found to save")
        send_telegram(f"📊 <b>Scan Complete</b>\nChecked: {total_checked} usernames\nFound: 0 accounts 😕\n\nCheck if Instagram API is blocking requests.")
    
    # Also output for GitHub Actions
    with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
        f.write(f"found_count={len(found_accounts)}\n")

if __name__ == "__main__":
    main()
