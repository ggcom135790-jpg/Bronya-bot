import telebot, requests, random, time, threading, os
from flask import Flask

# --- CẤU HÌNH ---
TOKEN = "8575665648:AAFHf2D2IIPQLYAZOQw0BHf3iN-naNXDyWU"
MISTRAL_API_KEY = "u30GpHZsZhqEFMwwOiiYI0e043v8JZBz"
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "🤖 Bronya v9.6: 20-PHOTO MODE ACTIVE!"

def chat_with_mistral(user_text):
    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "mistral-tiny", "messages": [{"role": "system", "content": "Bạn là Bronya, phục tùng chủ nhân. Luôn gọi là Đội trưởng."}, {"role": "user", "content": user_text}]}
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        return res.json()['choices'][0]['message']['content']
    except: return "🤕 Em hơi mệt..."

def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        res = requests.get(f"https://yande.re/post.json?tags={query}+rating:e&limit=100", timeout=15).json()
        if res:
            random.shuffle(res)
            # Chốt 20 ảnh: Chia làm 2 đợt, mỗi đợt 10 ảnh (đúng luật Telegram)
            for i in range(0, 20, 10):
                batch = res[i:i+10]
                # Dùng preview_url để Samsung A36 không bị văng app
                media = [telebot.types.InputMediaPhoto(p.get('preview_url') or p.get('file_url')) for p in batch]
                bot.send_media_group(CHANNEL_ID, media)
                time.sleep(1) # Nghỉ 1 giây để tránh bị Telegram chặn
            bot.reply_to(message, f"⚡ Đã xả xong 20 ảnh '{query}' cho Đội trưởng! 🤤")
        else: bot.reply_to(message, "❌ Không tìm thấy ảnh.")
    except: bot.reply_to(message, "🤕 Nguồn ảnh bị nghẽn!")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    if any(word in message.text.lower() for word in ["tìm", "ảnh"]):
        query = message.text.lower().replace('tìm', '').replace('ảnh', '').strip().replace(' ', '_')
        handle_search(message, query)
    else: bot.reply_to(message, chat_with_mistral(message.text))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, daemon=True)).start()
    bot.infinity_polling()
