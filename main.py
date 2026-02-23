import telebot, requests, threading, os, random, time
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Kho lưu trữ ảnh tạm thời để "vượt bão" IP
IMAGE_STORAGE = {} 

@app.route('/')
def health(): return "Storage System Online!", 200

SOURCES = [
    {"name": "Konachan", "url": "https://konachan.com/post.json?tags={tags}&limit=50"}, # Tải hẳn 50 tấm
    {"name": "Yande.re", "url": "https://yande.re/post.json?tags={tags}&limit=50"},
    {"name": "Rule34", "url": "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tags}&limit=50"}
]

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        tag = message.text.strip().lower().replace(" ", "_")
        bot.send_chat_action(message.chat.id, 'upload_photo')

        # 1. Nếu trong kho đã có sẵn ảnh từ lần tải trước, lấy ra dùng luôn
        if tag in IMAGE_STORAGE and len(IMAGE_STORAGE[tag]) >= 3:
            pics = [IMAGE_STORAGE[tag].pop() for _ in range(3)] # Lấy 3, còn lại vẫn lưu trong kho
            media = [telebot.types.InputMediaPhoto(url) for url in pics]
            bot.send_media_group(message.chat.id, media)
            bot.send_message(message.chat.id, f"📦 Lấy từ kho lưu trữ! (Còn dư {len(IMAGE_STORAGE[tag])} tấm)")
            return

        # 2. Nếu kho trống, đi tải 50 tấm mới
        random.shuffle(SOURCES)
        for src in SOURCES:
            api_url = src['url'].format(tags=tag)
            res = requests.get(api_url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                urls = [p.get('file_url') for p in data if p.get('file_url')]
                
                if len(urls) > 0:
                    random.shuffle(urls)
                    # Gửi 3 tấm cho Đội trưởng
                    to_send = urls[:3]
                    IMAGE_STORAGE[tag] = urls[3:] # Lưu 47 tấm còn lại vào kho
                    
                    media = [telebot.types.InputMediaPhoto(url) for url in to_send]
                    bot.send_media_group(message.chat.id, media)
                    bot.send_message(message.chat.id, f"🚀 Đã tải 50 ảnh mới! Đã gửi 3, lưu kho 47 tấm để né chặn IP.")
                    return
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Đội trưởng ơi, kho ảnh đang bị kẹt rồi!")

# ... (Giữ nguyên phần run và app.run như cũ)
