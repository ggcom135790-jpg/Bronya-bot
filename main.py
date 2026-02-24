import telebot, requests, random, time, threading, schedule, os, yt_dlp
from flask import Flask

# 1. PHẢI ĐỊNH NGHĨA BOT TRƯỚC
TOKEN = "8230688448:AAGto6RNTLJpD5jGWias1NlTF5VSrKjJdXA"
CHANNEL_ID = "-1003749427897" 
bot = telebot.TeleBot(TOKEN)

# 2. SAU ĐÓ MỚI DÙNG LỆNH CỦA BOT
bot.remove_webhook() 

# --- Các phần còn lại giữ nguyên ---
CHARACTERS = ["march_7th", "seele", "bronya_rand", "silver_wolf", "firefly", "acheron", "robin_honkai", "ganyu", "raiden_shogun", "kafka", "black_swan"]
history = set()

OBEDIENT_PHRASES = [
    "Tuân lệnh Đội trưởng, em thực hiện ngay đây... 💋",
    "Mọi mệnh lệnh của Đội trưởng đều là tuyệt đối.",
    "Ngài muốn em làm gì nữa không? Em đang đợi... 🤤",
    "Vâng ạ, em sẽ ngoan mà. Đội trưởng đừng giận em nhé?"
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'}

app = Flask(__name__)
@app.route('/')
def home(): return "🦾 Bronya v5.0: Ultimate Mode is Live!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# 📥 Tính năng Tải video
def download_video(url, message):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'max_filesize': 50 * 1024 * 1024
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video, caption="📽 Video của ngài đây ạ, Đội trưởng xem có thích không? 🤤")
        os.remove('video.mp4')
    except Exception:
        bot.reply_to(message, "🥺 Video nặng quá hoặc link lỗi, em không tải về được...")

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        text = message.text.lower()
        if "http" in text:
            bot.reply_to(message, "💋 Đội trưởng đợi em tải video về nhé...")
            threading.Thread(target=download_video, args=(message.text, message)).start()
            return
        if any(word in text for word in ["ơi", "ngoan", "nghe đây", "lệnh"]):
            bot.reply_to(message, random.choice(OBEDIENT_PHRASES))
            return
        name = text.replace('tìm','').replace('cho','').replace('ảnh','').strip().replace(' ', '_')
        target = name if (name and len(name) >= 2) else random.choice(CHARACTERS)
        bot.reply_to(message, f"🦋 Vâng, em đang săn ảnh '{target}' cho ngài...")
        url = f"https://yande.re/post.json?tags={target}&limit=100"
        data = requests.get(url, headers=HEADERS).json()
        pool = [p for p in data if p.get('id') not in history and 'file_url' in p]
        if pool:
            random.shuffle(pool)
            selected = pool[:5]
            media = [telebot.types.InputMediaPhoto(item['file_url']) for item in selected]
            bot.send_media_group(CHANNEL_ID, media)
            for item in selected: history.add(item['id'])
            bot.send_message(message.chat.id, f"✅ Xong rồi ạ! Ảnh '{target}' này Đội trưởng có ưng không? 🤤")
        else:
            bot.reply_to(message, f"⚠️ Em hết ảnh '{target}' mới rồi, ngài đổi nhân vật nhé?")
    except Exception:
        bot.reply_to(message, "🥺 Em vấp chân chút, ngài nhắn lại nhé?")

threading.Thread(target=run_web, daemon=True).start()
bot.infinity_polling()
