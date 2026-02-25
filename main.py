import telebot, requests, random, time, threading, os
from flask import Flask

TOKEN = "8575665648:AAH0U1xydQ6fVBWfSzm8rnLS0jDS9faoT8s" 
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "🦋 Seele Full HD: ONLINE!"

def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        src_url = f"https://yande.re/post.json?tags={query}+rating:e&limit=100"
        res = requests.get(src_url, timeout=15).json()
        if res:
            random.shuffle(res)
            for i in range(0, 20, 10):
                batch = res[i:i+10]
                # Dùng file_url để ảnh nét căng 4K
                media = [telebot.types.InputMediaPhoto(p.get('file_url')) for p in batch]
                bot.send_media_group(CHANNEL_ID, media)
                time.sleep(2)
            bot.reply_to(message, f"🦋 Seele xả xong 20 ảnh '{query}' siêu nét cho Đội trưởng! 🤤")
        else:
            bot.reply_to(message, f"❌ Không thấy ảnh '{query}' rồi...")
    except:
        bot.reply_to(message, "🤕 Đợi Seele tí nhé!")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text.lower()
    if any(word in text for word in ["tìm", "ảnh"]):
        query = text.replace('tìm', '').replace('ảnh', '').strip().replace(' ', '_')
        handle_search(message, query)

if __name__ == "__main__":
    # Đổi sang cổng 8000 để reset hệ thống
    port = int(os.environ.get("PORT", 8000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, daemon=True)).start()
    bot.infinity_polling()
