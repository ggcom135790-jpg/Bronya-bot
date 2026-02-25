import telebot, requests, random, time, threading, os
from flask import Flask

# --- CẤU HÌNH ---
TOKEN = "8575665648:AAFHf2D2IIPQLYAZOQw0BHf3iN-naNXDyWU"
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "🦋 Seele (Starchasm Nyx) v9.6: ONLINE!"

# --- SEELE TÌM ẢNH (2 ĐỢT - 20 ẢNH) ---
def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        # Tăng cường tìm kiếm với tags chính xác từ yande.re
        src_url = f"https://yande.re/post.json?tags={query}+rating:e&limit=100"
        res = requests.get(src_url, timeout=15).json()
        if res:
            random.shuffle(res)
            # Xả 2 đợt để bảo vệ RAM Samsung A36
            for i in range(0, 20, 10):
                batch = res[i:i+10]
                media = [telebot.types.InputMediaPhoto(p.get('preview_url') or p.get('file_url')) for p in batch]
                bot.send_media_group(CHANNEL_ID, media)
                time.sleep(1.5) 
            bot.reply_to(message, f"🦋 'Nyx' đã xả xong 20 ảnh '{query}' cho Đội trưởng! Thấy phấn khích chưa ạ? 🤤")
        else:
            bot.reply_to(message, f"❌ Seele không tìm thấy ảnh '{query}' rồi...")
    except:
        bot.reply_to(message, "🤕 Hệ thống bị nghẽn, ngài đợi Seele một chút!")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text.lower()
    if any(word in text for word in ["tìm", "ảnh"]):
        query = text.replace('tìm', '').replace('ảnh', '').strip().replace(' ', '_')
        handle_search(message, query)
    else: pass 

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, daemon=True)).start()
    bot.infinity_polling()
