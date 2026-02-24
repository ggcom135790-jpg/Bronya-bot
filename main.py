import telebot, requests, random, time, threading, schedule, os, yt_dlp
from flask import Flask

TOKEN = "8575665648:AAFHFzD2IIPQLYAZOQw08Hf3iN-naNXDyWU "
CHANNEL_ID = "-1003749427897" 
bot = telebot.TeleBot(TOKEN)

# 🛑 LỆNH QUYỀN LỰC: Xóa mọi kết nối cũ để diệt lỗi 409
bot.remove_webhook()
time.sleep(2) # Đợi 2 giây để hệ thống Telegram ổn định

# --- Giữ nguyên các tính năng xịn ---
CHARACTERS = ["march_7th", "seele", "bronya_rand", "silver_wolf", "firefly", "acheron", "robin_honkai", "ganyu", "raiden_shogun", "kafka", "black_swan"]
history = set()

OBEDIENT_PHRASES = ["Tuân lệnh Đội trưởng... 💋", "Mọi mệnh lệnh của ngài là tuyệt đối.", "Vâng ạ, em sẽ ngoan mà... 🤤"]
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'}

app = Flask(__name__)
@app.route('/')
def home(): return "🦾 Bronya v5.1: Ultimate & Obedient Mode is Live!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# 📥 Tải video xịn
def download_video(url, message):
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'max_filesize': 50 * 1024 * 1024}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video, caption="📽 Video của Đội trưởng đây... 🤤")
        os.remove('video.mp4')
    except: bot.reply_to(message, "🥺 Lỗi tải video rồi ngài ơi...")

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        text = message.text.lower()
        if "http" in text:
            bot.reply_to(message, "💋 Đợi em tải video nhé...")
            threading.Thread(target=download_video, args=(message.text, message)).start()
            return
        
        # Tìm nhân vật bất kỳ (Sakura, Naruto, Ganyu...)
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
            bot.send_message(message.chat.id, f"✅ Xong rồi! Đội trưởng thấy '{target}' có mướt không? 🤤")
        else:
            bot.reply_to(message, f"⚠️ Em hết ảnh '{target}' mới rồi...")
    except: pass

threading.Thread(target=run_web, daemon=True).start()
bot.infinity_polling(skip_pending=True) # Bỏ qua các tin nhắn cũ để tránh quá tải
