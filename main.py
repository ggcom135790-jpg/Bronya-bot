import telebot, requests, random, time, threading, os
from flask import Flask

TOKEN = "8575665648:AAFHf2D2IIPQLYAZOQw0BHf3iN-naNXDyWU"
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home():
    return "🤖 Bronya v9.2: FIX CONNECTION ERROR ACTIVE!"

# Danh sách nguồn ảnh - Đã thêm cơ chế ưu tiên nguồn khỏe
SOURCES = [
    "https://yande.re/post.json?tags={tags}+rating:e&limit=100",
    "https://konachan.com/post.json?tags={tags}+rating:e&limit=100"
]

@bot.message_handler(commands=['random', 'goiy'])
def suggest(message):
    tags = ["raiden_shogun", "ganyu", "yelan", "kafka", "firefly", "acheron", "hu_tao", "yae_miko"]
    pick = random.choice(tags)
    bot.reply_to(message, f"🎲 Gợi ý: {pick}. Đang bốc 10 ảnh...")
    handle_search(message, pick)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    text = message.text.lower()
    is_ai = "ai" in text
    search_query = text.replace('tìm', '').replace('ảnh', '').replace('r18', '').replace('ai', '').strip().replace(' ', '_')
    
    if not search_query: return
    
    final_query = f"{search_query}+ai_generated" if is_ai else search_query
    handle_search(message, final_query)

def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        
        # SỬA LỖI: Thêm Session để giữ kết nối ổn định hơn
        session = requests.Session()
        data = []
        
        # Thử nguồn ảnh ngẫu nhiên để tránh bị chặn
        src_url = random.choice(SOURCES).format(tags=query)
        try:
            res = session.get(src_url, timeout=20)
            if res.status_code == 200:
                data = res.json()
        except:
            # Nếu nguồn 1 lỗi, tự động nhảy sang nguồn 2 ngay
            alt_url = SOURCES[0].format(tags=query) if src_url != SOURCES[0] else SOURCES[1].format(tags=query)
            data = session.get(alt_url, timeout=20).json()

        if data:
            random.shuffle(data)
            selected = data[:10]
            media = []
            for p in selected:
                img_url = p.get('sample_url') or p.get('file_url')
                if img_url:
                    media.append(telebot.types.InputMediaPhoto(img_url))

            if media:
                # Gửi ảnh và đợi 2 giây để tránh lỗi Flood
                bot.send_media_group(CHANNEL_ID, media)
                time.sleep(2) 
                bot.reply_to(message, f"🔥 Xong! 10 ảnh về '{query}' đã nổ. Đội trưởng kiểm tra đi! 🤤")
            else:
                bot.reply_to(message, "🤫 Tìm thấy ảnh nhưng link bị lỗi, thử lại phát nữa nhé!")
        else:
            bot.reply_to(message, f"❌ Không tìm thấy gì cho '{query}'.")
            
        session.close() # Đóng kết nối sau khi dùng xong để giải phóng RAM
    except Exception as e:
        bot.reply_to(message, f"🤕 Lỗi rồi: {str(e)}. Đợi 5 giây rồi thử lại nhé!")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), daemon=True)).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=10) # Sửa lỗi bot tự ngắt kết nối
