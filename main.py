import telebot, requests, threading, os
from flask import Flask

# ⚙️ Cấu hình hệ thống
TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = "-1003749427897" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya Online & Ready!"

@bot.message_handler(func=lambda m: True)
def dual_engine_handler(message):
    msg = message.text.lower()
    tag = msg.replace('tìm','').replace('cho','').replace('ảnh','').replace('video','').replace('clip','').strip().replace(' ', '_')
    if len(tag) < 2: return

    # 🎬 SĂN VIDEO (Rule34)
    if any(word in msg for word in ['video', 'clip', 'vid']):
        bot.reply_to(message, f"🎬 Đang lùng CLIP '{tag}' từ Rule34...")
        url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}+file_ext:mp4&limit=3"
        try:
            data = requests.get(url, timeout=10).json()
            videos = [p.get('file_url') for p in data if p.get('file_url')]
            if videos:
                for v in videos: bot.send_video(CHANNEL_ID, v)
                bot.send_message(message.chat.id, "✅ Clip đã về kho lưu trữ!")
            else: bot.reply_to(message, "❌ Không tìm thấy clip nào.")
        except: bot.reply_to(message, "⚠️ Rule34 đang kẹt, thử lại sau nhé!")

    # 🖼️ SĂN ẢNH (Yande - 10 tấm)
    else:
        bot.reply_to(message, f"🚀 Đang gom 10 ảnh '{tag}' cực nét từ Yande...")
        url = f"https://yande.re/post.json?tags={tag}&limit=10"
        try:
            data = requests.get(url, timeout=10).json()
            urls = [p.get('sample_url') or p.get('file_url') for p in data]
            if urls:
                media = [telebot.types.InputMediaPhoto(u) for u in urls[:10]]
                bot.send_media_group(CHANNEL_ID, media)
                bot.send_message(message.chat.id, "✅
