import telebot, requests, random, time, threading, os, yt_dlp
from flask import Flask

TOKEN = "8575665648:AAFHFzD2IIPQLYAZOQw08Hf3iN-naNXDyWU".strip()
CHANNEL_ID = "-1003749427897" # <-- Đội trưởng kiểm tra kỹ ID này nhé!
bot = telebot.TeleBot(TOKEN)

# Diệt lỗi 409 triệt để
try:
    bot.remove_webhook()
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=True")
except: pass

CHARACTERS = ["march_7th", "seele", "bronya_rand", "silver_wolf", "firefly", "acheron", "robin_honkai", "ganyu", "raiden_shogun", "kafka", "black_swan"]
history = set()

app = Flask(__name__)
@app.route('/')
def home(): return "🦾 Bronya v6.0: Final Form is Live!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "💋 Bronya đã sẵn sàng! Ngài muốn tìm ảnh ai? (Ví dụ: tìm ảnh sakura)")

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        text = message.text.lower()
        if "tìm" not in text and "ảnh" not in text: return

        name = text.replace('tìm','').replace('cho','').replace('ảnh','').strip().replace(' ', '_')
        target = name if (name and len(name) >= 2) else random.choice(CHARACTERS)
        
        bot.reply_to(message, f"🦋 Đợi em chút, em đang gom ảnh '{target}' mướt nhất cho ngài...")

        url = f"https://yande.re/post.json?tags={target}&limit=100"
        data = requests.get(url, timeout=10).json()
        pool = [p for p in data if p.get('id') not in history and 'file_url' in p]
        
        if pool:
            random.shuffle(pool)
            selected = pool[:5]
            media = [telebot.types.InputMediaPhoto(item['file_url']) for item in selected]
            
            # GỬI ẢNH VÀ KIỂM TRA LỖI
            try:
                bot.send_media_group(CHANNEL_ID, media)
                for item in selected: history.add(item['id'])
                bot.send_message(message.chat.id, f"✅ Hàng về! Đội trưởng vào Channel xem '{target}' nhé! 🤤")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Lỗi gửi ảnh vào Channel: {str(e)}\n(Ngài đã thêm bot làm Admin Channel chưa?)")
        else:
            bot.reply_to(message, f"⚠️ Hết ảnh '{target}' mới rồi, em reset bộ nhớ đây!")
            history.clear()
    except Exception as e:
        bot.reply_to(message, f"🥺 Lỗi hệ thống: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
