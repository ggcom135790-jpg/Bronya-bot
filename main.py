import telebot, requests, threading, os, time, random
from flask import Flask

# Cấu hình cơ bản
TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = "-1003749427897" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya Yande Mode Online!"

@bot.message_handler(func=lambda m: True)
def speed_ai_handler(message):
    msg = message.text.lower()
    
    # 🧠 BỘ NÃO THÔNG MINH: Tránh tìm kiếm linh tinh
    chat_keywords = ['bao lâu', 'sao lâu', 'nhanh', 'chào', 'bronya', 'đợi']
    if any(word in msg for word in chat_keywords):
        bot.reply_to(message, "Em đây! Đội trưởng đợi em vài giây, em đang kết nối tới kho ảnh Yande để lấy hàng chất lượng cao cho anh đây! ⚡")
        return

    # 🚀 CHẾ ĐỘ TÌM KIẾM MỚI (Yande.re)
    tag = msg.replace('tìm','').replace('cho','').replace('ảnh','').strip().replace(' ', '_')
    if len(tag) < 2: return 

    bot.send_message(message.chat.id, f"🚀 Đã chuyển sang nguồn Yande! Đang lùng sục ảnh '{tag}' cực nét cho anh...")

    # Sử dụng API của Yande.re để tránh bị chặn IP như Rule34
    url = f"https://yande.re/post.json?tags={tag}&limit=3"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Lấy URL ảnh (ưu tiên ảnh sample để gửi nhanh hơn)
        urls = [p.get('sample_url') or p.get('file_url') for p in data if (p.get('sample_url') or p.get('file_url'))]
        
        if urls:
            media = [telebot.types.InputMediaPhoto(u) for u in urls[:3]]
            bot.send_media_group(CHANNEL_ID, media)
            bot.send_message(message.chat.id, "✅ Hàng Yande cực nét đã về kho rồi anh ơi!")
        else:
            bot.reply_to(message, "❌ Nguồn Yande cũng không có nhân vật này. Đội trưởng kiểm tra lại tên tiếng Anh xem sao?")
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "⚠️ Có vẻ IP server vẫn đang bị 'cấm túc'. Đội trưởng thử Restart lại Render để đổi IP nhé!")

def run(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run).start()
bot.infinity_polling()
