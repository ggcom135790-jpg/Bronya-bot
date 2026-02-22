import telebot, requests, threading, os, random
from flask import Flask

# Cổng kết nối để Render không báo lỗi Port
app = Flask(__name__)
@app.route('/')
def health(): return "Bronya is Online and Ready!", 200

# TOKEN CỦA NGÀI (Hãy giữ nguyên nếu nó đang hoạt động)
TOKEN = "8575665648:AAGkzWJ0eLoDpSUEuS_eGCn-fYC5NqpUS3k"
bot = telebot.TeleBot(TOKEN)

# Danh sách nhân vật để nút bấm ngẫu nhiên hoạt động hoàn hảo
CHAR_LIST = ["mona", "ganyu", "yelan", "raiden_shogun", "kokomi", "hu_tao", "shenhe", "eula", "nilou", "navia"]

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    msg_text = message.text.strip().lower()
    
    # 1. Xử lý riêng cho nút bấm Ngẫu nhiên
    if "ngẫu nhiên" in msg_text:
        target = random.choice(CHAR_LIST)
        bot.reply_to(message, f"🎲 Bronya chọn ngẫu nhiên cho ngài: **{target}**")
    else:
        # 2. Làm sạch từ khóa (bỏ /, bỏ lệnh tìm...)
        target = msg_text.split()[-1].replace("/", "").replace("x", "")

    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        # Giả lập trình duyệt để tránh bị kho ảnh chặn
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5"
        
        response = requests.get(api_url, headers=headers, timeout=10)
        data = response.json()
        
        # 3. Kiểm tra dữ liệu trước khi gửi để tránh lỗi 400
        if data and isinstance(data, list) and len(data) > 0:
            media = [telebot.types.InputMediaPhoto(p['file_url']) for p in r if 'file_url' in p]
            if media:
                bot.send_media_group(message.chat.id, media)
            else:
                bot.send_message(message.chat.id, f"⚠️ Tìm thấy dữ liệu nhưng không có liên kết ảnh: {target}")
        else:
            bot.send_message(message.chat.id, f"❌ Kho ảnh không tìm thấy kết quả cho: {target}")
            
    except Exception as e:
        # Chỉ in lỗi ra log Render để ngài theo dõi, không làm phiền người dùng
        print(f"Lỗi logic: {e}")

def run_bot():
    try:
        bot.remove_webhook()
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Lỗi Polling: {e}")

if __name__ == "__main__":
    # Chạy song song bot và web server
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
