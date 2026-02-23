import telebot, requests, threading, os, time, random
from flask import Flask

# TOKEN MỚI ngài vừa lấy từ BotFather
TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = "-1003749427897" # Đã chuẩn hóa ID cho Đội trưởng

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "AI-Loyalty System Online!"

# Phản hồi khi Đội trưởng ra lệnh chat
@bot.message_handler(func=lambda m: True)
def loyal_ai_handler(message):
    msg = message.text.lower()
    
    # AI phản hồi chat đơn giản để chứng minh độ "tuân lệnh"
    if any(word in msg for word in ['chào', 'hello', 'bronya']):
        bot.reply_to(message, "Bronya nghe rõ! Đội trưởng muốn săn tài liệu hay muốn tâm sự gì với tôi?")
        return

    # AI Tự nhận diện lệnh săn ảnh/video
    is_video = any(word in msg for word in ['vid', 'clip', 'video', 'phim'])
    # Tự lọc tên nhân vật từ câu nói của ngài
    tag = msg.replace('tìm','').replace('cho','').replace('ảnh','').replace('clip','').strip().replace(' ', '_')

    bot.send_message(message.chat.id, f"🫡 Tuân lệnh! AI đang lùng sục {tag} cho Đội trưởng...")

    # Nguồn dữ liệu mạnh mẽ
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}+sort:random+file_ext:mp4&limit=3" if is_video \
          else f"https://yande.re/post.json?tags={tag}+rating:explicit&limit=15"

    try:
        data = requests.get(url, timeout=15).json()
        urls = [p.get('file_url') for p in data if p.get('file_url')]
        
        if not urls:
            bot.reply_to(message, f"❌ AI lùng sục khắp nơi nhưng chưa thấy {tag}. Ngài có muốn đổi mục tiêu không?")
            return

        # Gửi media theo nhóm để an toàn
        random.shuffle(urls)
        limit = 2 if is_video else 8
        for i in range(0, min(len(urls), 16), limit):
            batch = urls[i:i+limit]
            media = [telebot.types.InputMediaVideo(u) if is_video else telebot.types.InputMediaPhoto(u) for u in batch]
            bot.send_media_group(CHANNEL_ID, media)
            time.sleep(4) # Nghỉ lâu hơn để tránh bị Telegram "soi"

        bot.send_message(message.chat.id, "✅ Nhiệm vụ hoàn thành! Tài liệu đã được chuyển vào kho.")
    except Exception:
        bot.reply_to(message, "⚠️ Có chút trục trặc đường truyền, nhưng AI sẽ không bỏ cuộc. Đội trưởng thử lại nhé!")

def run(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run).start()
bot.infinity_polling()
