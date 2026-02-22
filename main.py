import telebot, requests, threading, os, random, time
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya Anti-409 System Online!", 200

SOURCES = [
    {"name": "Rule34", "api": "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Konachan", "api": "https://konachan.com/post.json?tags="},
    {"name": "Yande.re", "api": "https://yande.re/post.json?tags="},
    {"name": "Gelbooru", "api": "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags="}
]

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    try:
        raw_text = message.text.strip().lower()
        is_r18 = "r18" in raw_text
        target = raw_text.replace("r18", "").replace("/", "").replace("tìm", "").strip().replace(" ", "_")
        if not target or "ngẫu nhiên" in target:
            target = random.choice(["raiden_shogun", "yelan", "mona", "tifa_lockhart"])

        bot.send_chat_action(message.chat.id, 'upload_photo')
        
        # Thử lần lượt các nguồn cho đến khi thành công
        random.shuffle(SOURCES) 
        success = False
        
        for source in SOURCES:
            try:
                search_tags = f"{target}+rating:explicit" if is_r18 else f"{target}+rating:general"
                api_url = f"{source['api']}{search_tags}&limit=20"
                
                response = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                posts = response.json()
                if not isinstance(posts, list): posts = posts.get('post', [])

                if posts:
                    random.shuffle(posts)
                    media = []
                    for p in posts[:3]: # Lấy 3 tấm cho nhẹ
                        url = p.get('file_url') or p.get('sample_url')
                        if url:
                            if url.startswith('//'): url = 'https:' + url
                            media.append(telebot.types.InputMediaPhoto(url))
                    if media:
                        bot.send_media_group(message.chat.id, media)
                        success = True
                        break # Tìm thấy ảnh rồi thì dừng vòng lặp
            except:
                continue # Nguồn này lỗi, thử nguồn tiếp theo
        
        if not success:
            bot.send_message(message.chat.id, f"❌ Tất cả nguồn ảnh đều đang chặn kết nối hoặc không có ảnh cho: {target}")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Lỗi hệ thống: {str(e)}")

def run():
    bot.remove_webhook()
    time.sleep(1) # Đợi 1 giây để tránh lỗi 409 khi khởi động lại
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
