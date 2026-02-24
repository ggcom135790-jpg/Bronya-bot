import telebot, requests, random, time, threading, os, yt_dlp
from flask import Flask

# --- Cấu hình ---
TOKEN = "8575665648:AAFHFzD2IIPQLYAZOQw08Hf3iN-naNXDyWU".strip()
CHANNEL_ID = "-1003749427897" # <-- Đội trưởng nhớ thay ID chuẩn sau khi check nhé!
bot = telebot.TeleBot(TOKEN)

# Diệt lỗi 409 cũ
bot.remove_webhook(drop_pending_updates=True)

history = set()
app = Flask(__name__)
@app.route('/')
def home(): return "🦾 Bronya v6.2: Image Fix Mode Live!"

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        # Mẹo lấy ID Channel: Nếu nhắn tin này TRONG channel, bot sẽ báo ID
        if message.chat.type in ['channel', 'group', 'supergroup'] and "check id" in message.text.lower():
            bot.reply_to(message, f"🆔 ID của nơi này là: {message.chat.id}")
            return

        text = message.text.lower()
        if "tìm" in text or "ảnh" in text:
            name = text.replace('tìm','').replace('cho','').replace('ảnh','').strip().replace(' ', '_')
            target = name if name else "raiden_shogun"
            bot.reply_to(message, f"🦋 Đang săn ảnh '{target}' bản nhẹ cho ngài...")

            url = f"https://yande.re/post.json?tags={target}&limit=100"
            data = requests.get(url, timeout=10).json()
            # Dùng 'sample_url' thay vì 'file_url' để tránh lỗi MEDIA_EMPTY
            pool = [p for p in data if p.get('id') not in history and 'sample_url' in p]
            
            if pool:
                random.shuffle(pool)
                selected = pool[:5]
                media = [telebot.types.InputMediaPhoto(item['sample_url']) for item in selected]
                
                try:
                    bot.send_media_group(CHANNEL_ID, media)
                    bot.send_message(message.chat.id, f"✅ Hàng mướt '{target}' đã về Channel! 🤤")
                    for item in selected: history.add(item['id'])
                except Exception as e:
                    bot.reply_to(message, f"❌ Vẫn lỗi gửi vào Channel: {str(e)}\n\n(ID hiện tại: {CHANNEL_ID})")
            else:
                bot.reply_to(message, "⚠️ Hết ảnh rồi ngài ơi!")
    except: pass

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    bot.infinity_polling()
