import telebot, requests, threading, os, random, time
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID') # Lấy từ Render ngài vừa dán

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya Archive Mode Online!", 200

SOURCES = [
    {"name": "Yande.re", "url": "https://yande.re/post.json?tags={tags}&limit=50"},
    {"name": "Safebooru", "url": "https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={tags}&limit=50"}
]

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        raw = message.text.strip().lower()
        if raw == "/start": return # Bỏ qua lệnh start
        
        is_r18 = "r18" in raw
        tag = raw.replace("r18", "").strip().replace(" ", "_")
        search_tag = f"{tag}+rating:explicit" if is_r18 else f"{tag}+rating:general"
        
        bot.send_chat_action(message.chat.id, 'upload_photo')
        random.shuffle(SOURCES)
        
        for src in SOURCES:
            api_url = src['url'].format(tags=search_tag)
            res = requests.get(api_url, timeout=15)
            if res.status_code == 200:
                urls = [p.get('file_url') for p in res.json() if p.get('file_url')]
                if len(urls) >= 3:
                    # Gửi 3 tấm xem trước
                    media = [telebot.types.InputMediaPhoto(u) for u in urls[:3]]
                    bot.send_media_group(message.chat.id, media)
                    bot.send_message(message.chat.id, f"✅ Đã tìm thấy! Bronya đang đẩy toàn bộ {len(urls)} tấm vào kho lưu trữ cho ngài...")

                    # Chạy ngầm việc lưu 50 ảnh vào nhóm
                    def archive():
                        for i in range(0, len(urls), 10):
                            try:
                                batch = [telebot.types.InputMediaPhoto(u) for u in urls[i:i+10]]
                                bot.send_media_group(CHANNEL_ID, batch)
                                time.sleep(3)
                            except: pass
                    threading.Thread(target=archive).start()
                    return
        bot.send_message(message.chat.id, "⚠️ IP đang bị nghẽn. Đội trưởng hãy nhấn 'Clear build cache' trên Render nhé!")
    except Exception as e: pass

def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
