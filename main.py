import telebot, requests, threading, os, random, time
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
# Bronya tự động xử lý ID để tránh lỗi thừa số 2 của Đội trưởng
raw_id = os.environ.get('CHANNEL_ID', '').strip()
CHANNEL_ID = "-1003749427897" if "3749427897" in raw_id else raw_id

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya Advanced System Online!"

@bot.message_handler(func=lambda m: True)
def handle(message):
    raw = message.text.strip().lower()
    if raw == "/start": return
    
    # Lệnh tìm Video/GIF: gõ "vid [tên]" (Ví dụ: vid raiden)
    is_video = raw.startswith("vid ")
    search_term = raw.replace("vid ", "") if is_video else raw
    tag = search_term.replace(" ", "_")
    
    bot.send_chat_action(message.chat.id, 'upload_video' if is_video else 'upload_photo')
    
    # Nguồn ảnh & Video an toàn
    source_url = f"https://yande.re/post.json?tags={tag}+rating:explicit&limit=20"
    if is_video:
        source_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}+sort:random+file_ext:mp4&limit=5"

    try:
        res = requests.get(source_url, timeout=15).json()
        urls = [p.get('file_url') for p in res if p.get('file_url')]
        random.shuffle(urls)
        
        if not urls:
            bot.reply_to(message, "❌ Bronya không tìm thấy tài liệu này...")
            return

        # Gửi theo đợt để an toàn (Ảnh: 10 tấm, Video: 2 cái)
        limit = 2 if is_video else 10
        for i in range(0, min(len(urls), 20), limit):
            batch = urls[i:i+limit]
            media = [telebot.types.InputMediaVideo(u) if is_video else telebot.types.InputMediaPhoto(u) for u in batch]
            bot.send_media_group(CHANNEL_ID, media)
            time.sleep(2) # Nghỉ 2s để tránh bị Telegram ban
            
        bot.send_message(message.chat.id, f"✅ Đã xả kho {tag} vào kho lưu trữ!")
    except Exception as e:
        bot.reply_to(message, "⚠️ Lỗi đường truyền, Đội trưởng hãy thử lại nhé!")

def run(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run).start()
bot.infinity_polling()
