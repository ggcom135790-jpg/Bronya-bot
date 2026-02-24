# Đội trưởng hãy đè đoạn này vào phần xử lý tin nhắn nhé:

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        text = message.text.lower()
        
        # Phản hồi nũng nịu khi được gọi
        if any(word in text for word in ["ơi", "ngoan", "nghe đây", "lệnh"]):
            bot.reply_to(message, random.choice(OBEDIENT_PHRASES))
            return

        # Xử lý tên nhân vật
        # Xóa các từ khóa thừa để lấy tên nhân vật chính xác
        name = text.replace('tìm','').replace('cho','').replace('ảnh','').strip().replace(' ', '_')
        
        if not name or len(name) < 2:
            # Nếu chỉ nhắn "tìm ảnh", bot chọn ngẫu nhiên trong list "vợ" có sẵn
            target = random.choice(CHARACTERS)
            bot.reply_to(message, f"🎲 Đội trưởng muốn bất ngờ sao? Để em chọn '{target}' cho ngài nhé...")
        else:
            # Nếu có tên (Sakura, Naruto...), bot sẽ tìm đúng tên đó
            target = name
            bot.reply_to(message, f"🦋 Tuân lệnh! Em đang săn ảnh '{target}' từ kho lưu trữ thế giới cho ngài...")

        # Truy vấn Yande với nhân vật bất kỳ
        url = f"https://yande.re/post.json?tags={target}&limit=100"
        data = requests.get(url, headers=HEADERS).json()
        
        # Lọc chống trùng tuyệt đối
        pool = [p for p in data if p.get('id') not in history and 'file_url' in p]
        
        if pool:
            random.shuffle(pool)
            selected = pool[:5]
            media = [telebot.types.InputMediaPhoto(item['file_url']) for item in selected]
            bot.send_media_group(CHANNEL_ID, media)
            for item in selected: history.add(item['id'])
            bot.send_message(message.chat.id, f"✅ Hàng về! Ảnh '{target}' này có làm Đội trưởng thích thú không? 🤤")
        else:
            # Thông báo khi không tìm thấy hoặc hết ảnh mới
            bot.reply_to(message, f"⚠️ Đội trưởng ơi, ảnh mới của '{target}' em tìm không thấy tấm nào mới cả. Ngài thử tên khác nhé? 🥺")
            
    except Exception:
        bot.reply_to(message, "🥺 Em lỡ tay làm rơi dữ liệu, Đội trưởng ra lệnh lại cho em nhé?")
