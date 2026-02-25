import telebot, requests, random, time, threading, os
from flask import Flask

# --- CẤU HÌNH LINH HỒN MỚI ---
TOKEN = "8575665648:AAH0U1xydQ6fVBWfSzm8rnLS0jDS9faoT8s" 
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "🦋 Seele Full HD: ONLINE!"

# --- SEELE XẢ ẢNH CHẤT LƯỢNG CAO ---
def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        # Tăng limit lên để lọc được nhiều ảnh đẹp hơn
        src_url = f"https://yande.re/post.json?tags={query}+rating:e&limit=100"
        res = requests.get(src_url, timeout=15).json()
        
        if res:
            random.shuffle(res)
            # Chia làm 2 đợt gửi để tránh làm Samsung A36 bị quá tải
            for i in range(0, 20, 10):
                batch = res[i:i+10]
                # Sử dụng 'file_url' thay vì 'preview_url' để có chất lượng nét nhất
                media = [telebot.types.InputMediaPhoto(p.get('file_url')) for p in batch]
                bot.send_media_group(CHANNEL_ID, media)
                time.sleep(2) # Đợi một chút để ảnh chất lượng cao kịp tải lên
            bot.reply_to(message, f"🦋 Seele đã dâng lên 20 ảnh '{query}' bản NÉT NHẤT cho Đội trưởng! 🤤")
        else:
            bot.reply_to(message, f"❌ Seele tìm khắp Biển Lượng Tử mà không thấy ảnh '{query}' rồi...")
    except Exception as e:
        bot.reply_to(message, "🤕 Nguồn ảnh đang nghẽn hoặc ảnh quá nặng, Đội trưởng thử lại nhé!")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text.lower()
    # Chỉ phản hồi khi có từ khóa "tìm" hoặc "ảnh"
    if any(word in text for word in ["tìm", "ảnh"]):
        query = text.replace('tìm', '').replace('ảnh', '').strip().replace(' ', '_')
        handle_search(message, query)
    else:
        pass 

if __name__ == "__main__":
    # Sử dụng cổng 8080 để khớp với cấu hình Koyeb của ngài
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, daemon=True)).start()
    bot.infinity_polling()
