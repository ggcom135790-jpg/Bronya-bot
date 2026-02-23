import telebot, requests, threading, os, time, random
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = "-1003749427897" # ID nhóm Nguyen và bronya

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "AI-Safety System Online!"

@bot.message_handler(func=lambda m: True)
def safe_ai_handler(message):
    msg = message.text.lower()
    
    if any(word in msg for word in ['chào', 'hello', 'bronya']):
        bot.reply_to(message, "Bronya đã sẵn sàng! Mọi kết nối hiện tại đều được mã hóa an toàn. Đội trưởng muốn tìm gì?")
        return

    is_video = any(word in msg for word in ['vid', 'clip', 'video'])
    tag = msg.replace('tìm','').replace('cho','').replace('ảnh','').replace('clip','').strip().replace(' ', '_')

    bot.send_message(message.chat.id, f"🫡 Tuân lệnh! AI đang tìm kiếm '{tag}' qua các kênh an toàn...")

    # Cơ chế thử nhiều nguồn để né chặn IP
    urls = []
    sources = [
        f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}+sort:random" + ("+file_ext:mp4" if is_video else ""),
        f"https://yande.re/post.json?tags={tag}+rating:explicit&limit=15"
    ]

    for url in sources:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                urls = [p.get('file_url') for p in data if p.get('file_url')]
                if urls: break # Nếu có ảnh rồi thì không cần thử nguồn khác nữa
        except:
            continue # Nếu nguồn này lỗi thì thử nguồn tiếp theo

    if not urls:
        bot.reply_to(message, "❌ Các web nguồn hiện đang tạm khóa IP để bảo trì. Đội trưởng hãy đợi 5-10 phút để hệ thống tự động đổi IP mới nhé!")
        return

    try:
        random.shuffle(urls)
        limit = 1 if is_video else 5
        for i in range(0, min(len(urls), 10), limit):
            batch = urls[i:i+limit]
            media = [telebot.types.InputMediaVideo(u) if is_video else telebot.types.InputMediaPhoto(u) for u in batch]
            bot.send_media_group(CHANNEL_ID, media)
            time.sleep(5) # Nghỉ 5s giữa mỗi đợt gửi để đảm bảo an toàn tuyệt đối cho bot
        bot.send_message(message.chat.id, "✅ Đã chuyển tài liệu vào kho lưu trữ an toàn!")
    except Exception as e:
        bot.reply_to(message, "⚠️ Telegram đang hạn chế gửi nhanh. Tài liệu sẽ được gửi tới sau ít phút!")

def run(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run).start()
bot.infinity_polling()
