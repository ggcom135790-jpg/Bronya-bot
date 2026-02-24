import telebot, requests, threading, os
from flask import Flask

# ⚙️ Cấu hình hệ thống
TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = "-1003749427897" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya Realbooru Mode Online!"

@bot.message_handler(func=lambda m: True)
def dual_engine_handler(message):
    msg = message.text.lower()
    # Lọc từ khóa tìm kiếm
    tag = msg.replace('tìm','').replace('cho','').replace('ảnh','').replace('video','').replace('clip','').strip().replace(' ', '_')
    if len(tag) < 2: return

    # 🎬 SĂN VIDEO (Nguồn Realbooru - Ổn định hơn)
    if any(word in msg for word in ['video', 'clip', 'vid']):
        bot.reply_to(message, f"🎬 Đang săn CLIP '{tag}' từ Realbooru...")
        # Sử dụng API Realbooru để lấy file mp4
        url = f"https://realbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={tag}+file_ext:mp4&limit=3"
        try:
            data = requests.get(url, timeout=10).json()
            videos = [p.get('file_url') for p in data if p.get('file_url')]
            if videos:
                for v in videos: 
                    # Đảm bảo URL có đủ tiền tố http nếu bị thiếu
                    video_url = v if v.startswith('http') else f"https:{v}"
                    bot.send_video(CHANNEL_ID, video_url)
                bot.send_message(message.chat.id, "✅ Clip đã nổ trong kho Nguyen và bronya!")
            else:
                bot.reply_to(message, "❌ Realbooru không tìm thấy clip nào cho nhân vật này.")
        except:
            bot.reply_to(message, "⚠️ Nguồn video đang bận, Đội trưởng thử lại sau nhé!")

    # 🖼️ SĂN ẢNH (Nguồn Yande - 5 tấm cực nét)
    else:
        bot.reply_to(message, f"🚀 Đang gom 5 ảnh '{tag}' cực nét từ Yande...")
        url = f"https://yande.re/post.json?tags={tag}&limit=5"
        try:
            data = requests.get(url, timeout=10).json()
            urls = [p.get('sample_url') or p.get('file_url') for p in data]
            if urls:
                media = [telebot.types.InputMediaPhoto(u) for u in urls[:5]]
                bot.send_media_group(CHANNEL_ID, media)
                bot.send_message(message.chat.id, "✅ Ảnh chất lượng cao đã về kho!")
            else:
                bot.reply_to(message, "❌ Không tìm thấy ảnh trên Yande.")
        except:
            bot.reply_to(message, "⚠️ Yande đang quá tải!")

# ⚡ PHẦN MỞ PORT CHO RENDER (Bắt buộc để tránh lỗi No open ports)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling()
