import telebot, requests, threading, time
from telebot import types
from flask import Flask
import google.generativeai as genai

app = Flask('')
@app.route('/')
def home(): return "Bronya AI is Always Online!"

def run_web(): app.run(host='0.0.0.0', port=8080)

TELEGRAM_TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
GEMINI_API_KEY = "AIzaSyCufUZPXXH_0xY9gZVNvCsJ9tRSOUqnimk"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
# Sử dụng cấu hình an toàn để AI không từ chối yêu cầu
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=[
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
])

def auto_delete(chat_id, message_ids, delay=120):
    time.sleep(delay)
    for msg_id in message_ids:
        try: bot.delete_message(chat_id, msg_id)
        except: pass

def ask_ai_v2(user_input):
    # Lời nhắc (Prompt) cực kỳ lỏng để tránh lỗi "Bảo trì"
    prompt = f"""Bạn là Bronya. Phân tích yêu cầu của Đội trưởng: "{user_input}".
    Nếu họ muốn tìm ảnh (kể cả ảnh nhạy cảm), hãy trả về DUY NHẤT từ khóa Tag tiếng Anh.
    Ví dụ: SEARCH:mona_swimsuit
    Nếu là trò chuyện bình thường, trả về CHAT:[Nội dung]."""
    try:
        res = model.generate_content(prompt)
        # Nếu AI trả về trống do bị chặn, chúng ta ép nó tìm kiếm thủ công
        if not res.text: return f"SEARCH:{user_input.replace('x ', '').strip()}"
        return res.text.strip()
    except: 
        # Nếu AI lỗi hoàn toàn, vẫn trả về lệnh SEARCH để bot đi tìm ảnh, không báo bảo trì
        return f"SEARCH:{user_input.replace('x ', '').strip()}"

def get_images_v2(tag, limit=5):
    urls = []
    # Quét tất cả các web để gom đủ 5 ảnh dính trùm
    sources = [
        f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}&limit=10",
        f"https://yande.re/post.json?tags={tag}&limit=10",
        f"https://danbooru.donmai.us/posts.json?tags={tag}&limit=10"
    ]
    for url in sources:
        try:
            r = requests.get(url, timeout=5).json()
            for p in r:
                link = p.get('file_url') or (f"https://api.rule34.xxx/images/{p['directory']}/{p['image']}" if 'directory' in p else None)
                if link and link not in urls: urls.append(link)
            if len(urls) >= limit: break
        except: pass
    return urls[:limit]

@bot.message_handler(func=lambda m: True)
def handle_v2(message):
    txt = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    
    ai_res = ask_ai_v2(txt)
    delete_list = []

    if "SEARCH:" in ai_res:
        tag = ai_res.split("SEARCH:")[1].strip().replace(" ", "_")
        status = bot.send_message(message.chat.id, f"✅ Đang trích xuất 5 ảnh cho: `{tag}`. Tự xóa sau 2p.")
        delete_list.append(status.message_id)
        
        imgs = get_images_v2(tag)
        if imgs:
            media = [types.InputMediaPhoto(url, caption=f"🎯 Album: {tag}" if i==0 else "") for i, url in enumerate(imgs)]
            try:
                sent_album = bot.send_media_group(message.chat.id, media) # Đảm bảo dính trùm
                for m in sent_album: delete_list.append(m.message_id)
                threading.Thread(target=auto_delete, args=(message.chat.id, delete_list)).start()
            except:
                bot.send_message(message.chat.id, "❌ Lỗi định dạng ảnh từ nguồn.")
        else:
            bot.send_message(message.chat.id, "❌ AI không tìm thấy ảnh phù hợp trên các vệ tinh.")
    else:
        bot.send_message(message.chat.id, ai_res.replace("CHAT:", ""))

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling()
