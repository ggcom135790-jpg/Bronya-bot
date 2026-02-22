import telebot, requests, threading, os
from flask import Flask

app = Flask(__name__)
@app.route('/')
def health(): return "Bronya is Live!", 200

TOKEN = "8575665648:AAGkzWJ0eLoDpSUEuS_eGCn-fYC5NqpUS3k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle(message):
    # Lấy từ cuối cùng để tìm kiếm
    target = message.text.split()[-1].lower()
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        # Giả lập trình duyệt xịn hơn để tránh bị chặn
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5"
        
        response = requests.get(api_url, headers=headers, timeout=15)
        data = response.json()
        
        # Kiểm tra danh sách ảnh có thực sự tồn tại không trước khi gửi
        if data and isinstance(data, list) and len(data) > 0:
            media = []
            for p in data:
                if 'file_url' in p:
                    media.append(telebot.types.InputMediaPhoto(p['file_url']))
            
            if media:
                bot.send_media_group(message.chat.id, media)
            else:
                bot.send_message(message.chat.id, f"⚠️ Tìm thấy dữ liệu nhưng không có URL ảnh cho: {target}")
        else:
            bot.send_message(message.chat.id, f"❌ Kho ảnh không trả về kết quả cho: {target}")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Lỗi kết nối: {str(e)}")

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
