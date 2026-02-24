import telebot, requests, threading, os

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = "-1003749427897" 

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def dual_engine_handler(message):
    msg = message.text.lower()
    
    # 🧠 Lọc từ khóa để lấy tên nhân vật
    tag = msg.replace('tìm','').replace('cho','').replace('ảnh','').replace('video','').replace('clip','').strip().replace(' ', '_')
    if len(tag) < 2: return

    # 🎬 TRƯỜNG HỢP TÌM VIDEO (Dùng Rule34)
    if any(word in msg for word in ['video', 'clip', 'vid']):
        bot.reply_to(message, f"🎬 Đang lùng sục CLIP '{tag}' từ kho Rule34 cho anh...")
        # Rule34 hỗ trợ lọc file_ext:mp4 để tìm video
        url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}+file_ext:mp4&limit=3"
        try:
            data = requests.get(url, timeout=10).json()
            videos = [p.get('file_url') for p in data if p.get('file_url')]
            if videos:
                for v in videos: bot.send_video(CHANNEL_ID, v)
                bot.send_message(message.chat.id, "✅ Clip đã về kho lưu trữ!")
            else:
                bot.reply_to(message, "❌ Không tìm thấy clip nào cho nhân vật này.")
        except:
            bot.reply_to(message, "⚠️ Kho clip Rule34 đang bảo trì, anh thử lại sau nhé!")

    # 🖼️ TRƯỜNG HỢP TÌM ẢNH (Dùng Yande - Gửi 10 tấm)
    else:
        bot.reply_to(message, f"🚀 Đang gom 10 ảnh '{tag}' cực nét từ Yande cho anh...")
        url = f"https://yande.re/post.json?tags={tag}&limit=10" # Đã nâng giới hạn lên 10
        try:
            data = requests.get(url, timeout=10).json()
            urls = [p.get('sample_url') or p.get('file_url') for p in data]
            if urls:
                # Chia làm 2 nhóm để gửi (Telegram giới hạn 10 file/album)
                media = [telebot.types.InputMediaPhoto(u) for u in urls[:10]]
                bot.send_media_group(CHANNEL_ID, media)
                bot.send_message(message.chat.id, "✅ 10 ảnh chất lượng cao đã cập bến!")
            else:
                bot.reply_to(message, "❌ Không tìm thấy ảnh trên Yande.")
        except:
            bot.reply_to(message, "⚠️ Yande đang quá tải, anh đợi xíu nhé!")

bot.infinity_polling()
