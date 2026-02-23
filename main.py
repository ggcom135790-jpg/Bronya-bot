import telebot, requests, threading, os, random, time
from flask import Flask

# Chìa khóa kết nối
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Kho lưu trữ ảnh để dùng dần, né chặn IP
IMAGE_STORAGE = {} 

@app.route('/')
def health(): return "Bronya Storage Online!", 200

# Các nguồn ảnh cực mạnh
SOURCES = [
    {"name": "Konachan", "url": "https://konachan.com/post.json?tags={tags}&limit=50"},
    {"name": "Yande.re", "url": "https://yande.re/post.json?tags={tags}&limit=50"},
    {"name": "Rule34", "url": "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tags}&limit=50"}
]

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        raw = message.text.strip().lower()
        is_r18 = "r18" in raw
        tag = raw.replace("r18", "").strip().replace(" ", "_")
        if not tag: tag = "raiden_shogun"
        search_tag = f"{tag}+rating:explicit" if is_r18 else f"{tag}+rating:general"
        
        bot.send_chat_action(message.chat.id, 'upload_photo')

        if search_tag in IMAGE_STORAGE and len(IMAGE_STORAGE[search_tag]) >= 3:
            pics = [IMAGE_STORAGE[search_tag].pop() for _ in range(3)] 
            media = [telebot.types.InputMediaPhoto(url) for url in pics]
            bot.send_media_group(message.chat.id, media)
            bot.send_message(message.chat.id, f"📦 Lấy từ kho lưu trữ! (Còn {len(IMAGE_STORAGE[search_tag])} tấm)")
            return

        random.shuffle(SOURCES)
        success = False
        for src in SOURCES:
            try:
                api_url = src['url'].format(tags=search_tag)
                res = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    posts = data if isinstance(data, list) else data.get('post', [])
                    urls = [p.get('file_url') for p in posts if p.get('file_url')]
                    if len(urls) >= 3:
                        random.shuffle(urls)
                        IMAGE_STORAGE[search_tag] = urls[3:]
                        media = [telebot.types.InputMediaPhoto(url) for url in urls[:3]]
                        bot.send_media_group(message.chat.id, media)
                        bot.send_message(message.chat.id, f"🚀 Tải 50 ảnh từ {src['name']}! Đã gửi 3, lưu kho 47.")
                        success = True; break
            except: continue
        if not success: bot.send_message(message.chat.id, "⚠️ IP Ohio đang bị chặn, hãy thử lại sau!")
    except Exception as e: bot.send_message(message.chat.id, f"❌ Lỗi: {str(e)}")

def run_bot():
    while True:
        try:
            bot.remove_webhook()
            bot.infinity_polling(skip_pending=True, timeout=20)
        except: time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
