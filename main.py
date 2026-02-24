import telebot, requests, random, time, threading, os
from flask import Flask

TOKEN = "8575665648:AAFHf2D2IIPQLYAZOQw0BHf3iN-naNXDyWU"
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

# Khắc phục triệt để lỗi 409 và Webhook
try:
    bot.remove_webhook()
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=True")
except:
    pass

app = Flask(__name__)
@app.route('/')
def home():
    return "🤖 Bronya v8.1: 10-IMAGE MODE IS LIVE!"

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        text = message.text.lower()
        search_query = text.replace('tìm', '').replace('ảnh', '').replace('r18', '').replace('cho', '').strip().replace(' ', '_')

        if not search_query:
            return

        bot.reply_to(message, f"🤖 Nhận lệnh! Bronya đang thâm nhập kho ảnh 'full không che' về '{search_query}' cho ngài... 🤤")

        # Lấy tối đa 100 kết quả để xáo trộn cho mới mẻ
        url = f"https://yande.re/post.json?tags={search_query}+rating:e&limit=100"
        data = requests.get(url, timeout=10).json()

        if data:
            random.shuffle(data)
            # NÂNG CẤP: Lấy đúng 10 ảnh như Đội trưởng yêu cầu
            selected = data[:10] 
            
            media = [telebot.types.InputMediaPhoto(p['sample_url']) for p in selected if 'sample_url' in p]

            if media:
                # Gửi cả cụm 10 ảnh vào Channel
                bot.send_media_group(CHANNEL_ID, media)
                bot.send_message(message.chat.id, f"🔥 Hàng cực nặng về '{search_query}' đã nổ ở Channel rồi ạ! Đội trưởng vào kiểm tra ngay! 🤤")
            else:
                bot.reply_to(message, "🤫 Tìm thấy ảnh nhưng link bị lỗi, để em thử lại...")
        else:
            bot.reply_to(message, f"❌ Bronya không tìm thấy ảnh R18 nào của '{search_query}'. Ngài thử gõ tên nhân vật khác xem?")
    except Exception as e:
        # Đã sửa lỗi chính tả reply_to ở đây
        bot.reply_to(message, f"🤕 Lỗi hệ thống: {str(e)}")

if __name__ == "__main__":
    # Chạy Flask ở Port 10000 để Koyeb báo Healthy
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), daemon=True)).start()
    bot.infinity_polling()
