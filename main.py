import telebot, requests, threading, os
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = "-1003749427897" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__) # Phải có Flask để Render mở Port

@app.route('/')
def health(): return "Bronya Online!"

@bot.message_handler(func=lambda m: True)
def dual_engine_handler(message):
    msg = message.text.lower()
    tag = msg.replace('tìm','').replace('cho','').replace('ảnh','').replace('video','').replace('clip','').strip().replace(' ', '_')
    if len(tag) < 2: return

    # 🎬 TÌM VIDEO (Rule34)
    if any(word in msg for word in ['video', 'clip', 'vid']):
        bot.reply_to(message, f"🎬 Đang lùng CLIP '{tag}'...")
        url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}+file_ext:mp4&limit=3"
        try:
            data = requests.get(url, timeout=10).json()
            videos = [p.get('file_url') for p in data if p.get('file_url')]
            if videos:
                for v in videos: bot.send_video(CHANNEL_ID, v)
                bot.send_message(message.chat.id, "✅ Clip đã về kho!")
            else: bot.reply_to(message, "❌ Không thấy clip.")
        except: bot.reply_to(message, "⚠️ Rule34 đang kẹt.")

    # 🖼️ TÌM ẢNH (Yande - 10 tấm)
    else:
        bot.reply_to(message, f"🚀 Đang gom 10 ảnh '{tag}'...")
        url = f"https://yande.re/post.json?tags={tag}&limit=10"
        try:
            data = requests.get(url, timeout=10).json()
            urls = [p.get('sample_url') or p.get('file_url') for p in data]
            if urls:
                media = [telebot.types.InputMediaPhoto(u) for u in urls[:10]]
                bot.send_media_group(CHANNEL_ID, media)
                bot.send_message(message.chat.id, "✅ 10 ảnh đã về kho!")
            else: bot.reply_to(message, "❌ Không thấy ảnh.")
        except: bot.reply_to(message, "⚠️ Yande đang bận.")

# ⚡ PHẦN QUAN TRỌNG: Mở Port đúng cách cho Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling(non_stop=True) # Chỉ để 1 dòng này ở cuối cùng thôi
