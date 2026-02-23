# Đoạn xử lý tìm kiếm thông minh hơn trong loyal_ai_handler:
try:
    # Thử nguồn dự phòng nếu nguồn chính báo lỗi đường truyền
    if is_video:
        url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}+file_ext:mp4&limit=3"
    else:
        # Chuyển sang nguồn Safebooru/Danbooru để né chặn IP
        url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={tag}&limit=10"
    
    response = requests.get(url, timeout=10)
    # Nếu bị chặn (status 403/429), AI sẽ tự báo cho ngài biết để đợi đổi IP
    if response.status_code != 200:
        bot.reply_to(message, "⚠️ Web nguồn đang bảo trì hoặc chặn IP, Đội trưởng hãy đợi 5 phút để Render đổi IP mới nhé!")
        return
