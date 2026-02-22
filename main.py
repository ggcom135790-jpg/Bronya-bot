import telebot, requests, threading, os, random
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def health(): return "Bronya Multi-Source R18 Online!", 200

SOURCES = [
    {"name": "Rule34", "api": "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Gelbooru", "api": "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Realbooru", "api": "https://realbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags="}
]

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    raw_text = message.text.strip().lower()
    is_r18 = "r18" in raw_text
    target = raw_text.replace("r18", "").replace("tìm", "").strip().replace(" ", "_")
    
    if not target or "ngẫu nhiên" in target:
        target = random.choice(["mona", "yelan", "tifa_lockhart", "raiden_shogun", "2b", "makima", "firefly_(honkai:_star_rail)"])

    bot.send_chat_action(message.chat.id, 'upload_photo')
    source = random.choice(SOURCES)
    random_page = random.randint(0, 20)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # SỬA LỖI TẠI ĐÂY: Dùng dấu + để API nhận diện đúng tag
        search_tags = f"{target}+rating:explicit" if is_r18 else f"{target}+rating:general"
        api_url = f"{source['api']}{search_tags}&limit=5&pid={random_page}"
        
        response = requests.get(api_url, headers=headers, timeout=15)
        data = response.json()
        posts = data if isinstance(data, list) else data.get('post', [])

        if posts:
            random.shuffle(posts)
            media = []
            for p in posts[:5]:
                url = p.get('file_url') or p.get('sample_url')
                if url:
                    if url.startswith('//'): url = 'https:' + url
                    media.append(telebot.types.InputMediaPhoto(url))
            bot.send_media_group(message.chat.id, media)
        else:
            bot.send_message(message.chat.id, f"❌ {source['name']} không tìm thấy ảnh cho: {target}")
    except:
        bot.send_message(message.chat.id, "⚠️ Nguồn ảnh đang bận, Đội trưởng thử lại nhé!")

def run():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
