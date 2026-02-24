import telebot, requests, random, time, threading, os
from flask import Flask

TOKEN = "8575665648:AAFHFzD2IIPQLYAZOQw08Hf3iN-naNXDyWU".strip()
CHANNEL_ID = "-1003749427897" 
bot = telebot.TeleBot(TOKEN)

# ✅ SỬA LỖI Ở ĐÂY: Xóa webhook thủ công để không bị lỗi "unexpected keyword" trên Render
try:
    bot.remove_webhook()
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=True")
except:
    pass
time.sleep(2)

app = Flask(__name__)
@app.route('/')
def home(): return "🦾 Bronya v7.1: R18 Unlocked & Bug Fixed!"

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        text = message.text.lower()
        # Loại bỏ từ thừa để lấy tag chuẩn
        search_query = text.replace('tìm','').replace('ảnh','').replace('r18','').replace('cho','').strip().replace(' ', '_')
        
        if not search_query: return
        
        bot.reply_to(message, f"🔞 Nhận lệnh! Bronya đang thâm nhập kho ảnh cực cháy về '{search_query}' cho ngài...")

        # Tìm ảnh với tag rating:q (Questionable - Rất gợi cảm)
        url = f"https://yande.re/post.json?tags={search_query}+rating:q&limit=50"
        data = requests.get(url, timeout=10).json()
        
        if data:
            random.shuffle(data)
            selected = data[:5]
            # Dùng sample_url để tải ảnh mượt, không bị lỗi nặng file
            media = [telebot.types.InputMediaPhoto(p['sample_url']) for p in selected if 'sample_url' in p]
            
            if media:
                bot.send_media_group(CHANNEL_ID, media)
                bot.send_message(message.chat.id, f"✅ Hàng cực phẩm về '{search_query}' đã nổ ở Channel rồi ạ! 🤤")
            else:
                bot.reply_to(message, "🥺 Em tìm thấy link nhưng ảnh bị lỗi hiển thị mất rồi...")
        else:
            bot.reply_to(message, f"❌ Bronya vẫn không thấy ảnh '{search_query}'. Đội trưởng chỉ cần gõ tên chuẩn (Ví dụ: raiden_shogun, yelan) là được nhé!")
    except Exception as e:
        bot.reply_to(message, f"🥺 Lỗi hệ thống: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    bot.infinity_polling()
