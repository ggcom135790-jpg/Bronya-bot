import telebot, requests, threading, os, random
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def health(): return "Bronya Multi-Source R18 Online!", 200

# Các nguồn ảnh R18 đa dạng
SOURCES = [
    {"name": "Rule34", "api": "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Gelbooru", "api": "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Realbooru", "api": "https://realbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags="}
]

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    raw_text = message.text.strip().lower()
    is_r18 = "r18" in raw_text
    
    # Làm sạch tên để tìm đa dạng nhân vật
    target = raw_text.replace("r18", "").replace("tìm", "").strip().replace(" ", "_")
    
    if not target or "ngẫu nhiên" in target:
        target = random.choice(["mona", "yelan", "tifa_lockhart", "raiden_shogun", "2b", "makima", "firefly_(honkai:_star_rail)"])

    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    # CHỐNG TRÙNG: Chọn ngẫu nhiên 1 trong 3 nguồn và 1 trang ngẫu nhiên (pid)
    source = random.choice(SOURCES)
    random_page = random.randint(0, 30)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        tags = f"{target} rating:explicit" if is_r18 else f"{target} rating:general"
        api_url = f"{source['api']}{tags}&limit=5&pid={random_page}"
        
        data = requests.get(api_url, headers=headers, timeout=15).json()
        posts = data if isinstance(data, list) else data.get('post', [])

        if posts:
            random.shuffle(posts) # Xáo trộn ảnh để không trùng
            media = []
            for p in posts[:5]:
                url = p.get('file_url') or p.get('sample_url')
                if url:
                    if url.startswith('//'): url = 'https:' + url
                    media.append(telebot.types.InputMediaPhoto(url))
            bot.send_media_group(message.chat.id, media)
        else:
            bot.send_message(message.chat.id, f"❌ {source['name']} không có ảnh cho: {target}. Thử lại lần nữa để bot đổi nguồn khác nhé!")
    except:
        bot.send_message(message.chat.id, "⚠️ Nguồn ảnh đang bảo trì, Đội trưởng đợi chút nhé!")

def run():
    bot.remove_webhook() # Diệt lỗi 409
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
