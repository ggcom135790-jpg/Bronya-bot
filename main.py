@bot.message_handler(func=lambda m: True)
def speed_ai_handler(message):
    msg = message.text.lower()
    
    # 1. Nếu là câu hỏi bình thường -> Chat trả lời ngay, KHÔNG tìm ảnh
    if any(word in msg for word in ['bao lâu', 'sao lâu', 'nhanh', 'chào', 'bronya']):
        bot.reply_to(message, "Anh đừng lo, em đang lọc ảnh chất lượng nhất cho anh đây. Đợi em vài giây thôi! ⚡")
        return

    # 2. Chỉ tìm ảnh khi ngài gõ đúng trọng tâm tên nhân vật
    is_video = any(word in msg for word in ['vid', 'clip'])
    # AI lọc bỏ các từ thừa để lấy đúng tên nhân vật
    tag = msg.replace('tìm','').replace('cho','').replace('ảnh','').strip().replace(' ', '_')

    bot.send_message(message.chat.id, f"🚀 Tăng tốc tìm {tag} cho Đội trưởng...")

    # Rút ngắn giới hạn ảnh xuống để gửi cực nhanh
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}" + ("+file_ext:mp4&limit=1" if is_video else "&limit=3")

    try:
        data = requests.get(url, timeout=5).json()
        urls = [p.get('file_url') for p in data if p.get('file_url')]
        
        if urls:
            media = [telebot.types.InputMediaPhoto(u) for u in urls[:3]]
            bot.send_media_group(CHANNEL_ID, media)
            bot.send_message(message.chat.id, "✅ Hàng về rồi nè anh!")
        else:
            bot.reply_to(message, "❌ Nguồn này kẹt rồi, anh thử tên khác nhé!")
    except:
        bot.reply_to(message, "⚠️ Web đang quá tải, anh đợi 1 phút rồi gõ lại nhé!")
