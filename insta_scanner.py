import requests
import uuid
import time
import random
import json
import string
import re
import os
import base64
import secrets
from datetime import datetime

# ========= متغيرات من Environment =========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ========= عداد =========
hits = 0
good = 0
bad = 0
total_checked = 0
found_accounts = []

# ========= جلسات =========
session = requests.Session()
google_session = requests.Session()

# ========= ثوابت =========
IG_APP_ID = "936619743392459"
IG_ANDROID_UA = "Instagram 370.1.0.43.96 Android (34/14; 450dpi; 1080x2207; samsung; SM-A235F; a23; qcom; en_IN; 704872281)"

# ========= قوائم لتوليد يوزرات واقعية =========
FIRST_NAMES = [
    "ahmed", "mohamed", "omar", "ali", "hassan", "hussain", "abdullah", "khaled",
    "youssef", "mahmoud", "mostafa", "ibrahim", "salah", "tamer", "nasser", "gamal",
    "john", "michael", "david", "james", "robert", "william", "daniel", "matthew",
    "sarah", "emma", "olivia", "ava", "sophia", "isabella", "mia", "charlotte",
    "lina", "noor", "sara", "mariam", "fatima", "haya", "layla", "amira",
    "kim", "lisa", "jennie", "jisoo", "rose", "jennifer", "jessica", "taylor"
]

LAST_NAMES = [
    "smith", "johnson", "williams", "brown", "jones", "garcia", "miller", "davis",
    "ali", "hassan", "hussein", "ahmed", "omar", "khaled", "mostafa", "salah",
    "kim", "park", "choi", "jung", "lee", "kang", "yoon", "jang"
]

INTERESTS = [
    "dev", "coder", "gamer", "pro", "king", "queen", "star", "life",
    "art", "photography", "travel", "music", "fitness", "food", "soccer",
    "real", "official", "world", "love", "happy", "fun", "cool", "vibe"
]

def random_username():
    """توليد يوزر انستغرام عشوائي واقعي"""
    patterns = [
        # اسم + أرقام
        lambda: random.choice(FIRST_NAMES) + str(random.randint(1, 9999)),
        # اسم_اسم
        lambda: random.choice(FIRST_NAMES) + "_" + random.choice(LAST_NAMES),
        # اسم + اهتمام
        lambda: random.choice(FIRST_NAMES) + "." + random.choice(INTERESTS),
        # نقطة بين الأسماء
        lambda: random.choice(FIRST_NAMES) + "." + random.choice(LAST_NAMES),
        # كلها أحرف صغيرة
        lambda: ''.join(random.choices(string.ascii_lowercase, k=random.randint(6, 12))),
        # أحرف + أرقام
        lambda: ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(7, 11))),
        # اسم + 3 أرقام
        lambda: random.choice(FIRST_NAMES) + str(random.randint(100, 999)),
        # تحت سطر + كلمة
        lambda: "_" + random.choice(INTERESTS) + str(random.randint(10, 99)),
    ]
    return random.choice(patterns)()

def get_user_info(username):
    """جلب معلومات حساب انستغرام"""
    try:
        headers = {
            'User-Agent': f"Instagram {random.randint(200,370)}.0.0.{random.randint(10,99)}.{random.randint(100,999)} Android (34/14; 450dpi; 1080x2207; samsung; SM-A235F; qcom; en_IN; {random.randint(100000000,999999999)})",
            'x-ig-app-id': IG_APP_ID,
        }
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('data', {}).get('user', {})
            if user and user.get('username'):
                return {
                    'pk': user.get('id'),
                    'username': user.get('username'),
                    'full_name': user.get('full_name', ''),
                    'follower_count': user.get('edge_followed_by', {}).get('count', 0),
                    'following_count': user.get('edge_follow', {}).get('count', 0),
                    'media_count': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                    'is_private': user.get('is_private', False),
                    'is_business': user.get('is_business_account', False),
                    'biography': user.get('biography', ''),
                    'profile_pic_url': user.get('profile_pic_url', ''),
                    'external_url': user.get('external_url', ''),
                }
        return None
    except:
        return None

def search_email_for_username(username):
    """البحث عن الإيميل المرتبط بحساب انستغرام"""
    try:
        android_id = "android-" + secrets.token_hex(8)
        device_id = str(uuid.uuid4())
        family_id = str(uuid.uuid4())
        
        url = "https://i.instagram.com/api/v1/bloks/async_action/com.bloks.www.caa.ar.search.async/"
        
        payload = {
            'params': json.dumps({
                "client_input_params": {
                    "aac": json.dumps({
                        "aac_init_timestamp": int(time.time()),
                        "aacjid": str(uuid.uuid4()),
                        "aaccs": secrets.token_urlsafe(32)
                    }),
                    "search_query": username,
                    "search_screen_type": "email_or_username",
                    "is_whatsapp_installed": 1,
                    "fetched_email_list": []
                },
                "server_params": {
                    "event_request_id": str(uuid.uuid4()),
                    "device_id": android_id,
                    "family_device_id": family_id,
                    "waterfall_id": str(uuid.uuid4()),
                    "login_surface": "login_home",
                    "access_flow_version": "pre_mt_behavior"
                }
            }),
            'bk_client_context': json.dumps({
                "bloks_version": "5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b",
                "styles_id": "instagram"
            }),
            'bloks_versioning_id': "5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b"
        }
        
        headers = {
            'User-Agent': IG_ANDROID_UA,
            'accept-language': 'en-IN, en-US',
            'x-bloks-version-id': '5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b',
            'x-fb-friendly-name': 'IgApi: bloks/async_action/com.bloks.www.caa.ar.search.async/',
            'x-ig-android-id': android_id,
            'x-ig-app-id': '567067343352427',
            'x-ig-device-id': device_id,
            'x-ig-family-device-id': family_id,
            'x-ig-timezone-offset': str(datetime.now().astimezone().utcoffset().total_seconds()),
            'x-mid': base64.urlsafe_b64encode(secrets.token_bytes(18)).decode().rstrip('='),
            'x-pigeon-rawclienttime': str(time.time()),
            'x-pigeon-session-id': f"UFS-{uuid.uuid4()}-0",
        }
        
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        
        if response.status_code == 200 and username.lower() in response.text.lower():
            # نبحث عن إيميل في الرد
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, response.text)
            for email in emails:
                if 'gmail' in email or 'yahoo' in email or 'outlook' in email:
                    return email
            # إذا ما لقينا إيميل صريح، نرجّع اليوزر كإيميل
            return f"{username}@gmail.com"
        
        return None
    except:
        return None

def send_to_telegram(account_info):
    """إرسال النتائج إلى تيليجرام"""
    if not BOT_TOKEN or not CHAT_ID:
        print("  ⚠️ BOT_TOKEN أو CHAT_ID غير مضبوطين")
        return False
    
    try:
        msg = f"""
📱 **حساب انستغرام موجود!**
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
**اليوزرنيم:** @{account_info.get('username', '')}
**الاسم:** {account_info.get('full_name', 'غير معروف')}
**الإيميل:** {account_info.get('email', 'غير معروف')}
**المتابعين:** {account_info.get('followers', 0):,}
**يتابع:** {account_info.get('following', 0):,}
**المنشورات:** {account_info.get('posts', 0):,}
**خاص:** {'🔒 نعم' if account_info.get('is_private') else '🔓 لا'}
**السيرة:** {account_info.get('biography', 'فارغة')[:100]}
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
🔗 https://www.instagram.com/{account_info.get('username', '')}
"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            'chat_id': CHAT_ID,
            'text': msg,
            'parse_mode': 'Markdown'
        }, timeout=10)
        return True
    except Exception as e:
        print(f"  ⚠️ فشل الإرسال إلى تيليجرام: {e}")
        return False

def scan_random_usernames(count=20):
    """فحص يوزرات عشوائية مولّدة"""
    global hits, good, bad, total_checked, found_accounts
    
    print(f"\n[+] بدء فحص {count} يوزر مولّد عشوائياً...")
    print(f"[+] بوت تيليجرام: {'✅ موجود' if BOT_TOKEN else '❌ غير موجود'}")
    print(f"[+] معرف الشات: {'✅ موجود' if CHAT_ID else '❌ غير موجود'}")
    print()
    
    for i in range(count):
        username = random_username()
        total_checked += 1
        
        print(f"[{i+1}/{count}] 🕵️ فحص: @{username}")
        
        try:
            # ننتظر شوي قبل كل طلب
            time.sleep(random.uniform(3, 7))
            
            # جلب معلومات الحساب
            user_info = get_user_info(username)
            
            if not user_info:
                bad += 1
                print(f"  ❌ لم يتم العثور على @{username}")
                continue
            
            # خلاص وجدنا حساب - نبحث عن الإيميل
            print(f"  ✅ حساب موجود! متابعين: {user_info.get('follower_count', 0):,}")
            
            email = search_email_for_username(username)
            
            if email:
                hits += 1
                good += 1
                
                account_data = {
                    'username': username,
                    'full_name': user_info.get('full_name', 'N/A'),
                    'email': email,
                    'followers': user_info.get('follower_count', 0),
                    'following': user_info.get('following_count', 0),
                    'posts': user_info.get('media_count', 0),
                    'is_private': user_info.get('is_private', False),
                    'is_business': user_info.get('is_business', False),
                    'biography': user_info.get('biography', 'فارغة'),
                }
                
                found_accounts.append(account_data)
                print(f"  📧 الإيميل: {email}")
                
                # إرسال إلى تيليجرام
                if BOT_TOKEN and CHAT_ID:
                    send_to_telegram(account_data)
                    print(f"  📬 تم الإرسال إلى تيليجرام ✅")
            else:
                print(f"  📧 الإيميل: {username}@gmail.com (تقديري)")
                hits += 1
                good += 1
                
                account_data = {
                    'username': username,
                    'full_name': user_info.get('full_name', 'N/A'),
                    'email': f"{username}@gmail.com",
                    'followers': user_info.get('follower_count', 0),
                    'following': user_info.get('following_count', 0),
                    'posts': user_info.get('media_count', 0),
                    'is_private': user_info.get('is_private', False),
                    'biography': user_info.get('biography', ''),
                }
                
                found_accounts.append(account_data)
                
                if BOT_TOKEN and CHAT_ID:
                    send_to_telegram(account_data)
                    print(f"  📬 تم الإرسال إلى تيليجرام ✅")
            
        except Exception as e:
            bad += 1
            print(f"  ⚠️ خطأ: {str(e)[:60]}")
            time.sleep(random.uniform(5, 10))
    
    # النتائج النهائية
    print(f"\n{'='*50}")
    print(f"✅ تم الانتهاء من فحص {count} يوزر!")
    print(f"📊 الإحصائيات:")
    print(f"   إجمالي: {total_checked}")
    print(f"   ✅ وجد: {hits}")
    print(f"   ❌ غير موجود: {bad}")
    print(f"💾 تم حفظ النتائج في found_accounts.json")
    
    # حفظ النتائج
    if found_accounts:
        with open('found_accounts.json', 'w', encoding='utf-8') as f:
            json.dump(found_accounts, f, indent=2, ensure_ascii=False)

# ========= MAIN =========
if __name__ == '__main__':
    print("""
╔══════════════════════════════════╗
║   Instagram Account Finder       ║
║   يولد يوزرات عشوائياً           ║
║   ويرسل النتائج إلى تيليجرام     ║
╚══════════════════════════════════╝
    """)
    
    # عدد اليوزرات اللي تبي تفحصها
    SCAN_COUNT = 15  # ← غيّر الرقم حسب ما تبي
    
    scan_random_usernames(SCAN_COUNT)
