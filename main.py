import telebot, requests, threading, time
from telebot import types
from flask import Flask
import google.generativeai as genai

app = Flask('')
@app.route('/')
def home(): return "Bronya AI God Mode is Active!"

def run_web(): app.run(host='0.0.0.0', port=8080)

# Cấu hình Tokens
TELEGRAM_TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
GEMINI_API_KEY = "AIzaSyCufUZPXXH_0xY9gZVNvCsJ9tRSOUqnimk"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
# Thiết lập tính cách AI lạnh lùng, thông minh của Bronya
model = genai.GenerativeModel('gemini-1.5-flash')

# --- BỘ NÃO PHÂN TÍCH AI ---
def analyze_with_ai(user_input):
    prompt = f"""
    Bạn là AI Bronya Zaychik. Phân tích câu nói của Đội trưởng: "{user_input}"
    1. Nếu họ muốn tìm ảnh (có từ 'x', 'tìm', 'cho xem', hoặc tên nhân vật), hãy trả về: SEARCH:[tag_tiếng_anh_chuẩn]
       Ví dụ: "x mona silme" -> SEARCH:mona_genshin_impact_slime
    2. Nếu họ chỉ trò chuyện, hãy trả về: CHAT:[Câu trả lời ngắn gọn, phong cách Bronya]
    Chỉ trả về đúng định dạng, không giải thích thêm.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except: return "CHAT:Hệ thống AI đang bảo trì, Đội trưởng."

# --- HỆ THỐNG QUÉT 5 ẢNH DÍNH TRÙM ---
def fetch_album(tag, is_nsfw=False, limit=5):
    urls = []
    # Quét đa nguồn: Danbooru, Yande.re, Konachan
    apis = [
        f"https://danbooru.donmai.us/posts.json?tags={tag}{'+rating:explicit' if is_nsfw else ''}&limit={limit}",
        f"https://yande.re/post.json?tags={tag}&limit={limit}",
        f"https://konachan.com/post.json?tags={tag}&limit={limit}"
    ]
    for api in apis:
        try:
            r = requests.get(api, timeout=5).json()
            for p in r:
                link = p.get('file_url')
                if link and link not in urls: urls.append(link)
            if len(urls) >= limit: break
        except: pass
    return urls[:limit]

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_txt = message.text
    is_nsfw = user_txt.lower().startswith('x ')
    bot.send_chat_action(message.chat.id, 'typing')
    
    # AI xử lý thông tin
    res = analyze_with_ai(user_txt)
    
    if res.startswith("SEARCH:"):
        target_tag = res.replace("SEARCH:", "").strip()
        bot.send_message(message.chat.id, f"🧬 AI đã nhận diện Tag: `{target_tag}`. Đang đóng gói Album...")
        
        images = fetch_album(target_tag, is_nsfw)
        if images:
            media = [types.InputMediaPhoto(url, caption=f"🎯 Kết quả AI cho: {target_tag}" if i == 0 else "") for i, url in enumerate(images)]
            bot.send_media_group(message.chat.id, media) # Gửi dính trùm
        else:
            bot.send_message(message.chat.id, f"❌ AI tìm khắp các vệ tinh nhưng không thấy ảnh cho: {target_tag}")
    else:
        # Trả lời trò chuyện phong cách AI
        bot.send_message(message.chat.id, res.replace("CHAT:", ""))

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=40)
