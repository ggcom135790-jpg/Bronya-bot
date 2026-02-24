import telebot, requests, threading, os, time, random
from flask import Flask

# Cấu hình cơ bản
TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = "-1003749427897" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya Speed Mode Online!"

@bot.message_handler(func=lambda m: True)
def speed_ai_handler(message):
    msg = message.text.lower()
    
    # 🧠 BỘ NÃO THÔNG MINH: Phân biệt Chat và Lệnh tìm
    chat_keywords = ['bao lâu', 'sao lâu', 'nhanh', 'chào', 'bronya', 'đợi']
    if any(word in msg for word in chat_keywords):
        bot.reply_to(message, "Em đây! Đường truyền đang hơi kẹt vì các web nguồn hay chặn IP. Anh đợi em vài phút, em đang lách luật để gửi ảnh cho anh đây! ⚡")
        return

    # 🚀 CHẾ ĐỘ TÌM KIẾM NHANH: Chỉ tìm khi ngài ra lệnh thực sự
    is_video = any(word in msg for word in ['vid', 'clip', 'video'])
    tag = msg.replace('tìm','').replace('cho','').replace('ảnh','').replace('clip','').strip().replace(' ', '_')

    if len(tag) < 2: return # Tránh tìm kiếm linh tinh khi ngài chỉ chat ngắn

    bot.send_message(message.chat.id, f"🚀 Tuân lệnh! Em đang dùng 'kênh ưu tiên' tìm {tag} cho anh...")

    # Giảm giới hạn để gửi cực nhanh, tránh bị Telegram treo
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}" + ("+file_ext:mp4&limit=1" if is_video else "&limit=3")

    try:
        data = requests.get(url, timeout=5).json()
        urls = [p.get('file_url') for p in data if p.get('file_url')]
        
        if urls:
            # Gửi ngay lập tức đợt đầu
            media = [telebot.types.InputMediaPhoto(u) for u in urls[:3]]
            bot.send_media_group(CHANNEL_ID, media)
            bot.send_message(message.chat.id, "✅ Hàng về trong kho rồi anh ơi!")
        else:
            bot.reply_to(message, "❌ Em lục tung cả kho mà chưa thấy nhân vật này. Anh thử tên khác xem?")
    except:
        bot.reply_to(message, "⚠️ Web nguồn đang 'khó ở', anh đợi 5 phút rồi gọi em tìm lại nhé!")

def run(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run).start()
bot.infinity_polling()
