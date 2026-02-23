@bot.message_handler(commands=['start'])
def start(m):
    # Lấy ID của nơi đang chat (Cá nhân hoặc Nhóm)
    chat_id = m.chat.id
    msg = (
        "✨ **Bronya Archive Mode Online!**\n\n"
        f"📍 **ID của cuộc trò chuyện này là:** `{chat_id}`\n"
        "----------------------------------\n"
        "👉 **Nhiệm vụ của Đội trưởng:**\n"
        "1. Copy dãy số trên (có cả dấu trừ nếu có).\n"
        "2. Dán vào mục Environment trên Render với Key là `CHANNEL_ID`.\n"
        "3. Cấp quyền Admin cho Bronya để bắt đầu xả kho ảnh!\n\n"
        "🎮 **Lệnh tìm kiếm:** Gõ tên nhân vật + r18 (VD: `Yelan r18`)"
    )
    bot.send_message(m.chat.id, msg, parse_mode='Markdown')
