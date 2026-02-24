import telebot, requests, random, time, threading, os
from flask import Flask

TOKEN = "8575665648:AAFHFzD2IIPQLYAZOQw08Hf3iN-naNXDyWU".strip()
CHANNEL_ID = "-1003749427897" 
bot = telebot.TeleBot(TOKEN)

# Khắc phục triệt để lỗi 409 và TypeError trên Render
try:
    bot.remove_webhook()
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=True")
except: pass

app = Flask(__name__)
@app.route('/')
def home(): return "🔞 Bronya v8.0: R18 EXPLICIT MODE IS LIVE!"

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        text = message.text.lower()
        # Tự động tối ưu tên nhân vật để tìm đúng tag
        search_query = text.replace('tìm','').replace('ảnh','').replace('r18','').replace('cho','').strip().replace(' ', '_')
        
        if not search_query: return
        
        bot.reply_to(message, f"🔞 Nhận lệnh! Bronya đang thâm nhập kho ảnh 'full không che' về '{search_query}' cho ngài... 🤤")

        # NÂNG CẤP: Dùng rating:e (Explicit) để lấy ảnh hở 100%
        url = f"https://yande.re/post.json?tags={search_query}+rating:e&limit=100"
        data = requests.get(url, timeout=10).json()
        
        if data:
            random.shuffle(data)
            selected = data[:5]
            # Sử dụng sample_url để load ảnh nhanh, tránh lỗi Webpage Media Empty
            media = [telebot.types.InputMediaPhoto(p['sample_url']) for p in selected if 'sample_url' in p]
            
            if media:
                bot.send_media_group(CHANNEL_ID, media)
                bot.send_message(message.chat.id, f"🔥 Hàng cực nặng về '{search_query}' đã nổ ở Channel rồi ạ! Đội trưởng vào kiểm tra ngay! 🤤")
            else:
                bot.reply_to(message, "🥺 Tìm thấy ảnh nhưng link bị lỗi, để em thử lại...")
        else:
            bot.reply_to(message, f"❌ Bronya không tìm thấy ảnh R18 nào của '{search_query}'. Ngài thử gõ tên nhân vật khác xem?")
    except Exception as e:
        bot.reply_to(message, f"🥺 Lỗi hệ thống: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    bot.infinity_polling()
