import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from deep_translator import GoogleTranslator

# وضعنا التوكن مباشرة هنا كما طلبت للتجربة
TOKEN = '8643162843:AAEL0siET9iYyam18hBbj-WDEEPbAbyi94Q'

# تهيئة البوت
bot = telebot.TeleBot(TOKEN)

# قاموس لتتبع حالة المستخدم (هل طلب ترجمة نص أم ملف؟)
user_states = {}

# دالة رسالة الترحيب والأزرار
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    btn_text = InlineKeyboardButton("ترجمة نص 📝", callback_data="trans_text")
    btn_file = InlineKeyboardButton("ترجمة ملف (TXT) 📁", callback_data="trans_file")
    markup.add(btn_text, btn_file)
    
    welcome_text = (
        "أهلاً بك في بوت الترجمة الاحترافي 🤖\n\n"
        "أنا هنا لترجمة النصوص والملفات من الإنجليزية إلى العربية.\n"
        "اختر ما تريد ترجمته من الأزرار بالأسفل:"
    )
    bot.reply_to(message, welcome_text, reply_markup=markup)

# دالة الاستجابة لضغط الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "trans_text":
        user_states[chat_id] = "waiting_for_text"
        bot.send_message(chat_id, "أرسل النص باللغة الإنجليزية الآن ✍️:")
    elif call.data == "trans_file":
        user_states[chat_id] = "waiting_for_file"
        bot.send_message(chat_id, "أرسل الملف النصي (بصيغة .txt) باللغة الإنجليزية 📄:")

# دالة معالجة النصوص
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.startswith('/'): 
        return # تجاهل الأوامر مثل /start

    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if state == "waiting_for_text":
        bot.send_message(chat_id, "جاري الترجمة... ⏳")
        try:
            # الترجمة من الإنجليزي للعربي
            translated = GoogleTranslator(source='en', target='ar').translate(message.text)
            bot.reply_to(message, f"**النص المترجم:**\n\n{translated}", parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, "❌ حدث خطأ أثناء الترجمة. الرجاء المحاولة لاحقاً.")
        
        user_states[chat_id] = None # تصفير الحالة بعد الانتهاء
    else:
        bot.reply_to(message, "الرجاء اختيار 'ترجمة نص' أو 'ترجمة ملف' من القائمة الرئيسية عبر إرسال /start.")

# دالة معالجة الملفات
@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if state == "waiting_for_file":
        try:
            # التحقق من نوع الملف
            file_extension = message.document.file_name.split('.')[-1].lower()
            if file_extension != 'txt':
                bot.reply_to(message, "عذراً، البوت يدعم حالياً ملفات النص (.txt) فقط ⚠️.")
                return

            bot.send_message(chat_id, "جاري تحميل وترجمة الملف... قد يستغرق هذا بعض الوقت ⏳")

            # تحميل الملف
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            original_text = downloaded_file.decode('utf-8')

            # تقسيم النص لتجنب تجاوز حدود الترجمة (حدود المترجم عادة 5000 حرف)
            chunks = [original_text[i:i+4000] for i in range(0, len(original_text), 4000)]
            translated_text = ""
            for chunk in chunks:
                translated_text += GoogleTranslator(source='en', target='ar').translate(chunk) + "\n"

            # حفظ الملف المترجم وإرساله
            translated_file_name = f"AR_{message.document.file_name}"
            with open(translated_file_name, 'w', encoding='utf-8') as f:
                f.write(translated_text)

            with open(translated_file_name, 'rb') as f:
                bot.send_document(chat_id, f, caption="تمت ترجمة الملف بنجاح! ✅")

            # حذف الملف من الخادم بعد إرساله لتوفير المساحة
            os.remove(translated_file_name)
            user_states[chat_id] = None

        except Exception as e:
            bot.reply_to(message, "❌ حدث خطأ أثناء معالجة الملف. تأكد أنه ملف نصي صالح ويحتوي على نصوص.")
    else:
        bot.reply_to(message, "الرجاء الضغط على 'ترجمة ملف' من القائمة الرئيسية أولاً عبر إرسال /start.")

# تشغيل البوت باستمرار وبقوة
if __name__ == "__main__":
    print("البوت يعمل الآن بنجاح... 🚀")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
  
