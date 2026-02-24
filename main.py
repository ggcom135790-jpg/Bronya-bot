import telebot, requests, random, time, threading, os, yt_dlp
from flask import Flask

# --- Cấu hình hệ thống ---
TOKEN = "8575665648:AAFHFzD2IIPQLYAZOQw08Hf3iN-naNXDyWU".strip()
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

# ✅ Cách xóa tin nhắn rác chuẩn để không bị lỗi TypeError
bot.remove_webhook()
requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=True")
time.sleep(2)

CHARACTERS = ["march_7th", "seele", "bronya_rand", "silver_wolf", "firefly", "acheron", "robin_honkai", "ganyu", "raiden_shogun", "kafka", "black_swan"]
history = set()

OBEDIENT_PHRASES = [
    "Tuân lệnh Đội trưởng, em thực hiện ngay đây... 💋",
    "Chỉ cần là ý muốn của ngài, em không bao giờ từ chối.",
    "Ngài muốn em làm gì nữa không? Em đang đợi... 🤤"
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'}

app = Flask(__name__)
@app.route('/')
def home(): return "🦾 Bronya v5.5: Ultimate Mode is Live!"

# --- Tính năng Tải Video ---
def download_video(url, message):
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'max_filesize': 50 * 1024 * 1024}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video, caption="📽 Video của Đội trưởng đây... 🤤")
        os.remove('video.mp4')
    except: bot.reply_to(message, "🥺 Link lỗi hoặc video nặng quá ngài ơi...")

# --- Xử lý lệnh tìm ảnh ---
@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        text = message.text.lower()
        if "http" in text:
            bot.reply_to(message, "💋 Đội trưởng đợi em tải video nhé...")
            threading.Thread(target=download_video, args=(message.text, message)).start()
            return
        if any(word in text for word in ["ơi", "ngoan", "lệnh"]):
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
            bot.send_message(message.chat.id, f"✅ Hàng về! Đội trưởng vào Channel xem '{target}' nhé! 🤤")
        else:
            bot.reply_to(message, f"⚠️ Em hết ảnh '{target}' mới rồi, em reset bộ nhớ đây!")
            history.clear()
    except Exception as e:
        bot.reply_to(message, "🥺 Em vấp chân chút, ngài nhắn lại nhé?")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
