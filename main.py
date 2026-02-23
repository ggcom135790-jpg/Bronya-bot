import telebot, requests, threading, os, random, time
from flask import Flask

# --- CẤU HÌNH HỆ THỐNG ---
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya Anti-Block Final Online!", 200

# Danh sách nguồn ảnh đã lọc bỏ những trang quá gắt
SOURCES = [
    {"name": "Konachan", "api": "https://konachan.com/post.json?tags="},
    {"name": "Yande.re", "api": "https://yande.re/post.json?tags="},
    {"name": "Safebooru", "api": "https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Lolibooru", "api": "https://lolibooru.moe/post.json?tags="},
    {"name": "Danbooru", "api": "https://danbooru.donmai.us/posts.json?tags="}
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "✨ Bronya đã sẵn sàng! Đội trưởng hãy gõ tên nhân vật (ví dụ: raiden_shogun r18) để bắt đầu.")

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    try:
        raw_text = message.text.strip().lower()
        is_r18 = "r18" in raw_text
        # Làm sạch từ khóa tìm kiếm
        target = raw_text.replace("r18", "").replace("/", "").strip().replace(" ", "_")
        
        if not target or "ngẫu nhiên" in target:
            target = random.choice(["raiden_shogun", "yelan", "tifa_lockhart", "yae_miko", "furina"])

        bot.send_chat_action(message.chat.id, 'upload_photo')
        random.shuffle(SOURCES) 
        success = False
        
        for source in SOURCES:
            try:
                # Thiết lập tag R18 tùy theo nguồn
                tag_filter = "rating:explicit" if is_r18 else "rating:general"
                if source['name'] == "Danbooru":
                    tag_filter = "rating:e" if is_r18 else "rating:s"
                
                api_url = f"{source['api']}{target}+{tag_filter}&limit=20"
                
                response = requests.get(api_url, headers=HEADERS, timeout=10)
                if response.status_code != 200: continue
                
                posts = response.json()
                if not isinstance(posts, list):
                    posts = posts.get('post', []) or posts.get('posts', [])

                if posts:
                    random.shuffle(posts)
                    media = []
                    for p in posts[:3]:
                        # Lấy URL ảnh và xử lý định dạng //
                        img_url = p.get('file_url') or p.get('sample_url') or p.get('large_file_url')
                        if img_url:
                            if img_url.startswith('//'): img_url = 'https:' + img_url
                            media.append(telebot.types.InputMediaPhoto(img_url))
                    
                    if media:
                        bot.send_media_group(message.chat.id, media)
                        success = True
                        break 
            except Exception:
                continue
        
        if not success:
            bot.send_message(message.chat.id, "❌ Đội trưởng ơi, các nguồn ảnh vẫn đang chặn IP này. Ngài hãy đổi 'Region' trong Settings của Render sang 'Ohio (US)' hoặc 'Frankfurt' để có IP mới nhé!")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Lỗi: {str(e)}")

def run_polling():
    while True:
        try:
            bot.remove_webhook()
            time.sleep(2) # Chống lỗi 409
            bot.infinity_polling(skip_pending=True, timeout=20)
        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
