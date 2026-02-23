import telebot, requests, threading, os, random, time
from flask import Flask
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CẤU HÌNH HỆ THỐNG ---
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya Omega System Online!", 200

# Tạo Session với cơ chế tự động thử lại (Retry) khi gặp lỗi kết nối
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

SOURCES = [
    {"name": "Rule34", "api": "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Gelbooru", "api": "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Realbooru", "api": "https://realbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Konachan", "api": "https://konachan.com/post.json?tags="},
    {"name": "Yande.re", "api": "https://yande.re/post.json?tags="},
    {"name": "Safebooru", "api": "https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags="}
]

# Danh sách User-Agent để "xoay tua" giả danh nhiều thiết bị khác nhau
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'
]

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    try:
        raw_text = message.text.strip().lower()
        is_r18 = "r18" in raw_text
        target = raw_text.replace("r18", "").replace("/", "").strip().replace(" ", "_")
        
        if not target or "ngẫu nhiên" in target:
            target = random.choice(["raiden_shogun", "yelan", "tifa_lockhart", "yae_miko"])

        bot.send_chat_action(message.chat.id, 'upload_photo')
        random.shuffle(SOURCES)
        success = False
        
        for source in SOURCES:
            try:
                tag_r18 = "rating:explicit" if is_r18 else "rating:general"
                api_url = f"{source['api']}{target}+{tag_r18}&limit=25"
                
                # Sử dụng session và xoay tua User-Agent
                resp = session.get(api_url, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=12)
                
                if resp.status_code == 200:
                    posts = resp.json()
                    if not isinstance(posts, list): posts = posts.get('post', []) or posts.get('posts', [])
                    
                    if posts:
                        random.shuffle(posts)
                        media = []
                        for p in posts[:3]:
                            url = p.get('file_url') or p.get('sample_url')
                            if url:
                                if url.startswith('//'): url = 'https:' + url
                                media.append(telebot.types.InputMediaPhoto(url))
                        
                        if media:
                            bot.send_media_group(message.chat.id, media)
                            success = True; break
                time.sleep(0.5) # Nghỉ ngắn để tránh bị nghi ngờ spam
            except Exception: continue
        
        if not success:
            bot.send_message(message.chat.id, "❌ Các nguồn ảnh vẫn đang chặn IP của Render. Đội trưởng hãy nhấn 'Suspend' rồi 'Resume' trên web Render để đổi IP mới nhé!")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Lỗi: {str(e)}")

def run_bot():
    while True:
        try:
            bot.remove_webhook()
            time.sleep(2)
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception: time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
