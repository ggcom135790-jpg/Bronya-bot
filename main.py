import telebot, requests, threading, time, random
from telebot import types
from flask import Flask
import google.generativeai as genai

app = Flask('')
@app.route('/')
def home(): return "Bronya Zalo-Style is Online!"

def run_web(): app.run(host='0.0.0.0', port=8080)

# Cấu hình bảo mật
TELEGRAM_TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
GEMINI_API_KEY = "AIzaSyCufUZPXXH_0xY9gZVNvCsJ9tRSOUqnimk"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# Mở khóa toàn bộ để không bao giờ bị báo "Bảo trì"
safety = [
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety)

# --- TÍNH NĂNG TỰ TIÊU HỦY 2 PHÚT ---
def auto_delete(chat_id, message_ids, delay=120):
    time.sleep(delay)
    for msg_id in message_ids:
        try: bot.delete_message(chat_id, msg_id)
        except: pass

# --- BỘ NÃO AI "GÕ GÌ RA NẤY" ---
def master_ai_logic(user_input):
    prompt = f"""Bạn là Bronya. Phân tích ý định của Đội trưởng: "{user_input}"
    - Nếu họ nhắc đến tên nhân vật, ảnh, hoặc từ lóng (kể cả R18), trả về: SEARCH:[tag_tiếng_anh]
    - Nếu họ chỉ chào hỏi hoặc nói chuyện phiếm, trả về: CHAT:[câu trả lời lạnh lùng, thông minh]
    Ví dụ: "tìm yelan đi bơi" -> SEARCH:yelan_swimsuit
    Ví dụ: "mona gợi cảm" -> SEARCH:mona_genshin_impact_sexually_explicit
    """
    try:
        res = model.generate_content(prompt)
        return res.text.strip() if res.text else f"SEARCH:{user_input.replace(' ', '_')}"
    except:
        return f"SEARCH:{user_input.replace(' ', '_')}"

# --- HỆ THỐNG TRÍCH XUẤT ẢNH TỔNG LỰC ---
def get_album_master(tag, limit=5):
    all_urls = []
    # Quét đồng thời 3 vệ tinh lớn nhất
    apis = [
        f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}&limit=20",
        f"https://yande.re/post.json?tags={tag}&limit=20",
        f"https://danbooru.donmai.us/posts.json?tags={tag}&limit=20"
    ]
    for api in apis:
        try:
            r = requests.get(api, timeout=5).json()
            for p in r:
                link = p.get('file_url') or (f"https://api.rule34.xxx/images/{p['directory']}/{p['image']}" if 'directory' in p else None)
                # Lọc định dạng chuẩn để không bị lỗi
                if link and any(link.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                    if link not in all_urls: all_urls.append(link)
            if len(all_urls) >= 10: break
        except: pass
    
    random.shuffle(all_urls) # Làm mới kết quả mỗi lần gõ
    return all_urls[:limit]

@bot.message_handler(func=lambda m: True)
def handle_master(message):
    txt = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    
    ai_out = master_ai_logic(txt)
    to_delete = [message.message_id] # Xóa cả tin nhắn của người dùng nếu muốn

    if "SEARCH:" in ai_out:
        target = ai_out.split("SEARCH:")[1].strip().replace(" ", "_")
        status = bot.send_message(message.chat.id, f"🎯 Đang quét dữ liệu cho: `{target}`...")
        to_delete.append(status.message_id)
        
        imgs = get_album_master(target)
        if imgs:
            # Gửi Album 5 ảnh dính trùm
            media = [types.InputMediaPhoto(url, caption=f"✅ Gõ gì ra nấy: {target}" if i==0 else "") for i, url in enumerate(imgs)]
            try:
                sent_album = bot.send_media_group(message.chat.id, media)
                for m in sent_album: to_delete.append(m.message_id)
                # Kích hoạt tự xóa sau 2 phút
                threading.Thread(target=auto_delete, args=(message.chat.id, to_delete)).start()
            except:
                bot.send_message(message.chat.id, "❌ Lỗi đóng gói Album. Đội trưởng thử lại nhé.")
        else:
            bot.send_message(message.chat.id, f"❌ Bronya lục tung vệ tinh nhưng không thấy ảnh: {target}")
    else:
        bot.send_message(message.chat.id, ai_res.replace("CHAT:", ""))

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling()
