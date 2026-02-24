import telebot, requests, random, time, threading, schedule, os
from flask import Flask

# 🤖 Bronya System: Render Cloud Edition (Safe Mode)
TOKEN = "8230688448:AAGto6RNTLJpD5jGWias1NlTF5VSrKjJdXA"
CHANNEL_ID = "-1003749427897" 
bot = telebot.TeleBot(TOKEN)

CHARACTERS = ["march_7th", "seele", "bronya_rand", "silver_wolf", "firefly", "acheron", "robin_honkai"]
history = set()
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'}

print("--- 🦾 Bronya System v2.0: Render Cloud Khởi Động ---")

# 1. 🌐 Web Server ảo để Render không báo lỗi Timeout
app = Flask(__name__)
@app.route('/')
def home():
    return "🦾 Bronya System is running on Render!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. 🌅 Tính năng báo thức buổi sáng
def morning_routine():
    target = random.choice(CHARACTERS)
    try:
        url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=20"
        data = requests.get(url, headers=HEADERS, timeout=15).json()
        
        pool = []
        for p in data:
            pid = p.get('id')
            purl = p.get('file_url') or p.get('sample_url')
            if pid not in history and purl:
                if not purl.startswith('http'): purl = "https:" + purl
                pool.append((pid, purl))
        
        if pool:
            img = random.choice(pool)
            history.add(img[0])
            bot.send_photo(CHANNEL_ID, img[1], caption=f"🌅 Chào buổi sáng Đội trưởng! Báo thức nghệ thuật hôm nay của ngài là {target.replace('_', ' ').title()} nhé!")
    except:
        pass

# Render dùng múi giờ UTC. 00:00 UTC = 07:00 Sáng Việt Nam
schedule.every().day.at("00:00").do(morning_routine)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

# 3. 🔎 Tính năng tìm ảnh thủ công
@bot.message_handler(func=lambda m: True)
def handle(message):
    text = message.text.lower()
    target = text.replace('tìm','').replace('cho','').replace('ảnh','').strip().replace(' ', '_')
    
    if not target or len(target) < 2:
        target = random.choice(CHARACTERS)
    
    bot.reply_to(message, f"🦾 Bronya đang truy xuất ảnh an toàn cho: '{target}'...")

    try:
        url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=30"
        data = requests.get(url, headers=HEADERS, timeout=15).json()
        
        pool = []
        for p in data:
            pid = p.get('id')
            purl = p.get('file_url') or p.get('sample_url')
            if pid not in history and purl:
                if not purl.startswith('http'): purl = "https:" + purl
                pool.append((pid, purl))
        
        if pool:
            random.shuffle(pool)
            selected = pool[:5]
            media = [telebot.types.InputMediaPhoto(item[1]) for item in selected]
            bot.send_media_group(CHANNEL_ID, media)
            for item in selected: history.add(item[0])
            bot.reply_to(message, f"✅ Truy xuất thành công 5 ảnh mới.")
        else:
            bot.reply_to(message, "⚠️ Cảnh báo: Không tìm thấy ảnh mới/an toàn. Hãy thử nhân vật khác.")
    except:
        bot.reply_to(message, "❌ Lỗi hệ thống: Kết nối web nguồn bị ngắt.")

# 🚀 Khởi động đồng loạt các luồng
threading.Thread(target=run_web, daemon=True).start()
threading.Thread(target=run_scheduler, daemon=True).start()
bot.infinity_polling()
