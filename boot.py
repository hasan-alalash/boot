from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from PIL import Image
import io

LOGO_PATH = "logo.png"

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace('%', '')
    if text.isdigit():
        size = int(text)
        if 10 <= size <= 100:
            context.user_data['logo_size'] = size
            await update.message.reply_text(f"✅ سيتم استخدام حجم {size}% من **عرض الصورة** عند إضافة اللوغو.\nالآن أرسل الصورة.")
        else:
            await update.message.reply_text("⚠️ الرجاء اختيار رقم بين 10 و100.")
    else:
        await update.message.reply_text("❗ أرسل رقم الحجم كنسبة مئوية، مثل 30 أو 50 أو 75.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    size_percent = context.user_data.get('logo_size', 100)  # الافتراضي = 100% من عرض الصورة

    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    image_bytes = await photo_file.download_as_bytearray()

    try:
        original_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        logo = Image.open(LOGO_PATH).convert("RGBA")

        w_img, h_img = original_image.size

        # ضبط عرض اللوغو ليساوي عرض الصورة * النسبة المئوية المطلوبة
        new_logo_width = int(w_img * (size_percent / 100))
        logo_ratio = logo.height / logo.width
        new_logo_height = int(new_logo_width * logo_ratio)

        resized_logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)

        # مكان وضع اللوغو (أسفل الصورة)
        x = (w_img - new_logo_width) // 2  # غالبًا يكون صفر لأن العرضين متساويين
        y = h_img - new_logo_height        # أسفل الصورة

        # دمج الصورة واللوغو
        combined = original_image.copy()
        combined.paste(resized_logo, (x, y), resized_logo)

        # حفظ الصورة النهائية
        output = io.BytesIO()
        combined.convert("RGB").save(output, format="JPEG")
        output.seek(0)

        await update.message.reply_photo(photo=output, caption="✅ تمت إضافة اللوغو بعرض الصورة من الأسفل بنجاح!")

    except Exception as e:
        await update.message.reply_text(f"⚠️ حدث خطأ أثناء المعالجة:\n{e}")

if __name__ == "__main__":
    TOKEN = "8026294925:AAFtqcUPLrh-Gke9GsPIrxQLTf5kltf9zM0"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 البوت شغال...")
    app.run_polling()
