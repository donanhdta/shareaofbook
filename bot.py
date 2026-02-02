import telebot

bot = telebot.TeleBot("8253784016:AAHE_iK2jrohiDlVI_uSeSSwdwHKjfeDzfo")

user_data = {}

@bot.message_handler(commands=['share'])
def start_share(message):
    bot.reply_to(message, "1. Vui lòng gửi COOKIE (Lấy từ Business Suite):")
    bot.register_next_step_handler(message, get_cookie)

def get_cookie(message):
    user_data[message.chat.id] = {'cookie': message.text.strip().replace(" ", "")} # Tự xóa khoảng trắng lỗi
    bot.reply_to(message, "2. Vui lòng gửi UID bài viết:")
    bot.register_next_step_handler(message, get_uid)

def get_uid(message):
    user_data[message.chat.id]['uid'] = message.text.strip()
    bot.reply_to(message, "3. Vui lòng gửi SỐ LƯỢNG share (Ví dụ: 100):")
    bot.register_next_step_handler(message, get_amount)

def get_amount(message):
    try:
        user_data[message.chat.id]['amount'] = int(message.text.strip())
        bot.reply_to(message, "4. Vui lòng gửi DELAY (Ví dụ: 1):")
        bot.register_next_step_handler(message, get_delay)
    except:
        bot.reply_to(message, "Lỗi! Số lượng phải là số. Nhập lại số lượng:")
        bot.register_next_step_handler(message, get_amount)

def get_delay(message):
    try:
        data = user_data[message.chat.id]
        delay = int(message.text.strip())
        bot.reply_to(message, f"🚀 Đang bắt đầu buff {data['amount']} share cho ID {data['uid']}...")
        # Gọi hàm buff của bạn ở đây với: data['cookie'], data['uid'], data['amount'], delay
    except:
        bot.reply_to(message, "Lỗi! Delay phải là số. Nhập lại delay:")
        bot.register_next_step_handler(message, get_delay)

bot.polling()
