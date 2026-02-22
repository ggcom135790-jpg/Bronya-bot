import telebot, requests, time
from telebot import types

# TOKEN MỚI CỦA ĐỘI TRƯỞNG
TOKEN = "8575665648:AAFxvxgoqfHrVjE-gAcwlH6m3BlbgBkwP2k"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    # Chỉ lấy từ cuối cùng của tin nhắn để làm tag (Ví dụ: "ảnh mona" -> "mona")
    user_input = message.text.split()
    target_tag = user_input[-1].lower() if user_input else "anime"
    
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        # Gọi vệ tinh Rule34 lấy ảnh chất lượng cao
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target_tag}&limit=5"
        response = requests.get(api_url, timeout=10).json()
        
        urls = [p['file_url'] for p in response if 'file_url' in p and p['file_url'].endswith(('.jpg', '.png'))]
        
        if urls:
            media = [types.InputMediaPhoto(url, caption=f"✅ Bronya đã tìm thấy: {target_tag}" if i==0 else "") for i, url in enumerate(urls)]
            bot.send_media_group(message.chat.id, media)
        else:
            bot.send_message(message.chat.id, f"❌ Không tìm thấy ảnh cho tag: `{target_tag}`. Đội trưởng thử tên khác nhé!")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Lỗi kết nối máy chủ ảnh hoặc sai định dạng.")

if __name__ == "__main__":
    # Xóa sạch mọi yêu cầu cũ bị kẹt trước đó
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
