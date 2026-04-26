import telebot
from telebot import types
from deep_translator import GoogleTranslator
import fitz  # مكتبة PyMuPDF للتعامل مع الـ PDF
import os

# تم دمج التوكن الخاص بك هنا بنجاح
API_TOKEN = '8643162843:AAEL0siET9iYyam18hBbj-WDEEPbAbyi94Q'
bot = telebot.TeleBot(API_TOKEN)

# دالة لإنشاء الأزرار التفاعلية
def main_menu():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🌐 ترجمة نص مباشر", callback_data="tr_text")
    btn2 = types.InlineKeyboardButton("📄 ترجمة ملف PDF", callback_data="tr_pdf")
    markup.add(btn1, btn2)
    return markup

# الاستجابة عند إرسال أمر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك! أنا بوت الترجمة المطور 🚀\nاختر ماذا تريد أن تفعل الآن:", reply_markup=main_menu())

# التعامل مع ضغطات الأزرار (النص أو الملف)
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "tr_text":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "أرسل النص الذي تريد ترجمته إلى العربية:")
    elif call.data == "tr_pdf":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "أرسل ملف الـ PDF الآن وسأقوم باستخراج النص وترجمته لك.")

# معالجة ملفات الـ PDF المرفوعة
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.mime_type == 'application/pdf':
        msg = bot.reply_to(message, "جاري معالجة الملف وترجمته... انتظر قليلاً ⏳")
        
        # تحميل الملف من سيرفرات تليجرام
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # حفظ الملف مؤقتاً لمعالجته
        with open("input.pdf", 'wb') as f:
            f.write(downloaded_file)
        
        try:
            # استخراج النص من صفحات الـ PDF
            doc = fitz.open("input.pdf")
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()

            if not full_text.strip():
                bot.reply_to(message, "عذراً، الملف يبدو فارغاً أو يحتوي على صور فقط ولا يمكن استخراج نص منه.")
                return

            # ترجمة النص المستخرج للعربية (بحد أقصى 4500 حرف)
            translator = GoogleTranslator(source='auto', target='ar')
            translated_text = translator.translate(full_text[:4500])
            
            # حفظ النتيجة في ملف نصي وإرساله للمستخدم
            with open("translated.txt", "w", encoding="utf-8") as f:
                f.write(translated_text)
            
            with open("translated.txt", "rb") as f:
                bot.send_document(message.chat.id, f, caption="✅ تمت ترجمة النص المستخرج من الملف بنجاح.")
            
        except Exception as e:
            bot.reply_to(message, f"حدث خطأ أثناء المعالجة: {e}")
        finally:
            # تنظيف الملفات المؤقتة بعد الانتهاء
            if os.path.exists("input.pdf"): os.remove("input.pdf")
            if os.path.exists("translated.txt"): os.remove("translated.txt")
    else:
        bot.reply_to(message, "عذراً، أقبل ملفات PDF فقط.")

# ترجمة أي رسالة نصية عادية يتم إرسالها
@bot.message_handler(func=lambda message: True)
def translate_text(message):
    try:
        translated = GoogleTranslator(source='auto', target='ar').translate(message.text)
        bot.reply_to(message, f"الترجمة للعربية:\n\n{translated}")
    except:
        bot.reply_to(message, "عذراً، حدث خطأ في محرك الترجمة.")

# بدء تشغيل البوت واستقبال الرسائل
bot.polling()
