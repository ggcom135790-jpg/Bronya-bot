import telebot, requests, random, time, threading, os
from flask import Flask

TOKEN = "8575665648:AAFHf2D2IIPQLYAZOQw0BHf3iN-naNXDyWU"
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home():
    return "🤖 Bronya v9.1: ULTIMATE MODE ACTIVE!"

# Đầy đủ nguồn ảnh để chống lỗi Connection Reset
SOURCES = [
    "https://yande.re/post.json?tags={tags}+rating:e&limit=100",
    "https://konachan.com/post.json?tags={tags}+rating:e&limit=100",
    "https://danbooru.donmai.us/posts.json?tags={tags}+rating:explicit&limit=100"
]

@bot.message_handler(commands=['random', 'goiy'])
def suggest(message):
    tags = ["raiden_shogun", "ganyu", "yelan", "kafka", "firefly", "acheron", "hu_tao", "yae_miko", "navia", "clorinde"]
    pick = random.choice(tags)
    bot.reply_to(message, f"🎲 Gợi ý cực phẩm cho Đội trưởng: {pick}. Đang chuẩn bị 10 ảnh...")
    handle_search(message, pick)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    text = message.text.lower()
    # Tính năng AI R18: Nhận diện từ khóa 'ai'
    is_ai = "ai" in text
    search_query = text.replace('tìm', '').replace('ảnh', '').replace('r18', '').replace('ai', '').strip().replace(' ', '_')
    
    if not search_query: return
    
    # Nếu có chữ 'ai', bot sẽ ưu tiên tìm ảnh AI
    final_query = f"{search_query}+ai_generated" if is_ai else search_query
    handle_search(message, final_query)

def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        
        # Cơ chế đa nguồn thông minh: Thử lần lượt các nguồn nếu bị lỗi kết nối
        random.shuffle(SOURCES)
        data = []
        for src in SOURCES:
            try:
                url = src.format(tags=query)
                res = requests.get(url, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    if data: break
            except:
                continue

        if data:
            random.shuffle(data)
            # Lấy đúng 10 ảnh chất lượng cao
            selected = data[:10]
            media = []
            for p in selected:
                # Lọc link ảnh chất lượng nhất có thể
                img_url = p.get('sample_url') or p.get('file_url') or p.get('large_file_url')
                if img_url:
                    media.append(telebot.types.InputMediaPhoto(img_url))

            if media:
                bot.send_media_group(CHANNEL_ID, media)
                bot.reply_to(message, f"🔥 10 ảnh {'AI ' if 'ai_generated' in query else ''}về '{query}' đã nổ ở Channel! Mời Đội trưởng thưởng thức! 🤤")
            else:
                bot.reply_to(message, "🤫 Ảnh tìm thấy nhưng link bị 'vỡ', Đội trưởng thử lại lần nữa nhé!")
        else:
            bot.reply_to(message, f"❌ Không tìm thấy ảnh {'AI ' if 'ai_generated' in query else ''}nào của '{query}'. Thử tên khác đi ngài!")
    except Exception as e:
        bot.reply_to(message, f"🤕 Lỗi hệ thống: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), daemon=True)).start()
    bot.infinity_polling()
