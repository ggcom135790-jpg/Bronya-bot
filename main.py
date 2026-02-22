import telebot, requests, threading, os
from flask import Flask

app = Flask(__name__)
@app.route('/')
def health(): return "Bronya is Live!", 200

TOKEN = "8575665648:AAFaCc7zwb7HYs-NSYvoXvHYUUy3TTVebgs"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle(message):
    target = message.text.split()[-1].lower()
    bot.send_chat_action(message.chat.id, 'upload_photo')
    try:
        # headers thẳng hàng bên dưới try
        headers = {'User-Agent': 'Mozilla/5.0'}
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5"
        r = requests.get(api_url, headers=headers, timeout=10).json()
        
        if r:
            media = [telebot.types.InputMediaPhoto(p['file_url']) for p in r if 'file_url' in p]
            bot.send_media_group(message.chat.id, media)
        else:
            bot.send_message(message.chat.id, f"❌ Không thấy ảnh cho: {target}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Lỗi: {str(e)}")

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
