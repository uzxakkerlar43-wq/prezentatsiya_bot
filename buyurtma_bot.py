"""
Prezentatsiya buyurtmalarini qabul qiluvchi Telegram bot.
Adminga murojaat, chek takrorlanishini oldini olish, fayl yuborish bilan.
"""

import logging
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# ====== SOZLAMALAR ======
BOT_TOKEN = "8573836600:AAHgqwEqXFzUGejOvUZSDwd-ByQtQCUMX2Y"
ADMIN_ID = 7374195060  # Sizning Telegram ID raqamingiz
KARTA_RAQAMI = "5614 6812 9071 6020"
# ========================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

FAN, MAVZU, SLAYD, TIL, MUDDAT, TASDIQ, ADMINGA_YOZISH = range(7)

# Asosiy menyu (Adminga murojaat tugmasi bilan)
ASOSIY_MENYU = [
    ["📋 Prezentatsiya buyurtma berish"],
    ["👨‍💻 Adminga murojaat"]
]

SLAYD_TUGMALAR = [["10", "20", "50"], ["Boshqa son"], ["🔙 Ortga"]]
TIL_TUGMALAR = [["O'zbek", "Rus", "Ingliz"], ["🔙 Ortga"]]
TASDIQ_TUGMALAR = [["Ha, yuborish", "Bekor qilish"]]

MAX_SLAYD = 50

NARXLAR = [
    (10, 3000),
    (20, 5000),
    (50, 15000),
]

ISHLATILGAN_CHEKLAR = set()


def narx_hisobla(slayd_soni: int) -> int:
    for limit, narx in NARXLAR:
        if slayd_soni <= limit:
            return narx
    return NARXLAR[-1][1]


def som(summa: int) -> str:
    return f"{summa:,}".replace(",", " ") + " so'm"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Assalomu alaykum! Prezentatsiya buyurtma berish botiga xush kelibsiz.\n\n"
        "Quyidagi tugmalar yordamida buyurtma berishingiz yoki adminga murojaat qilishingiz mumkin:",
        reply_markup=ReplyKeyboardMarkup(ASOSIY_MENYU, resize_keyboard=True),
    )
    return ConversationHandler.END


async def buyurtma_boshlash(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Prezentatsiya narxlari:\n"
        f"• 10 tagacha slayd: {som(NARXLAR[0][1])}\n"
        f"• 20 tagacha slayd: {som(NARXLAR[1][1])}\n"
        f"• 50 tagacha slayd: {som(NARXLAR[2][1])}\n\n"
        "Bekor qilish uchun istalgan payt /cancel yozing.\n\n"
        "1/5. Qaysi fandan? (masalan: Anatomiya)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return FAN


async def adminga_murojaat_boshlash(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Admin uchun savol yoki murojaatingizni yozib yuboring. Tez orada javob beramiz:",
        reply_markup=ReplyKeyboardMarkup([["🔙 Ortga"]], resize_keyboard=True),
    )
    return ADMINGA_YOZISH


async def adminga_xabar_jonatish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "🔙 Ortga":
        await start(update, context)
        return ConversationHandler.END

    user = update.effective_user
    username = f"@{user.username}" if user.username else "username yo'q"

    xabar = (
        "<b>YANGI MUROJAAT!</b> ✉️\n\n"
        f"<b>Kimdan:</b> {user.full_name} ({username})\n"
        f"<b>ID:</b> <code>{user.id}</code>\n"
        f"<b>Profil:</b> tg://user?id={user.id}\n\n"
        f"<b>Xabar:</b> {text}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=xabar, parse_mode="HTML")
    await update.message.reply_text(
        "Murojaatingiz adminga yuborildi! Tez orada javob qaytaramiz.",
        reply_markup=ReplyKeyboardMarkup(ASOSIY_MENYU, resize_keyboard=True),
    )
    return ConversationHandler.END


async def fan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "🔙 Ortga":
        return await start(update, context)
    context.user_data["fan"] = text
    await update.message.reply_text("2/5. Mavzu nomini yozing:")
    return MAVZU


async def mavzu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "🔙 Ortga":
        await update.message.reply_text("1/5. Qaysi fandan?")
        return FAN
    context.user_data["mavzu"] = text
    await update.message.reply_text(
        "3/5. Nechta slayd kerak?",
        reply_markup=ReplyKeyboardMarkup(
            SLAYD_TUGMALAR, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return SLAYD


async def slayd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "🔙 Ortga":
        await update.message.reply_text("2/5. Mavzu nomini yozing:")
        return MAVZU
    if text == "Boshqa son":
        await update.message.reply_text(
            "Slaydlar sonini raqam bilan yozing (1 dan 50 gacha):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return SLAYD
    if not text.isdigit() or not (1 <= int(text) <= MAX_SLAYD):
        await update.message.reply_text(
            f"Iltimos, 1 dan {MAX_SLAYD} gacha bo'lgan raqamni kiriting."
        )
        return SLAYD
    context.user_data["slayd"] = text
    await update.message.reply_text(
        "4/5. Qaysi tilda bo'lsin?",
        reply_markup=ReplyKeyboardMarkup(
            TIL_TUGMALAR, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return TIL


async def til(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "🔙 Ortga":
        await update.message.reply_text(
            "3/5. Nechta slayd kerak?",
            reply_markup=ReplyKeyboardMarkup(
                SLAYD_TUGMALAR, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return SLAYD
    context.user_data["til"] = text
    await update.message.reply_text(
        "5/5. Qachongacha kerak? (masalan: 15-oktabr yoki 3 kun ichida)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return MUDDAT


async def muddat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "🔙 Ortga":
        await update.message.reply_text(
            "4/5. Qaysi tilda bo'lsin?",
            reply_markup=ReplyKeyboardMarkup(
                TIL_TUGMALAR, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return TIL
    context.user_data["muddat"] = text
    d = context.user_data
    narx = som(narx_hisobla(int(d["slayd"])))
    await update.message.reply_text(
        "Buyurtmangizni tekshiring:\n\n"
        f"• Fan: {d['fan']}\n"
        f"• Mavzu: {d['mavzu']}\n"
        f"• Slaydlar: {d['slayd']} ta\n"
        f"• Til: {d['til']}\n"
        f"• Muddat: {d['muddat']}\n"
        f"• Narx: {narx}\n\n"
        "Ma'lumotlar to'g'rimi? Yuboraylikmi?",
        reply_markup=ReplyKeyboardMarkup(
            TASDIQ_TUGMALAR, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return TASDIQ


async def tasdiq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text != "Ha, yuborish":
        return await cancel(update, context)

    d = context.user_data
    user = update.effective_user
    username = f"@{user.username}" if user.username else "username yo'q"
    narx = som(narx_hisobla(int(d["slayd"])))

    xabar = (
        "<b>YANGI BUYURTMA!</b> 📥\n\n"
        f"<b>Mijoz:</b> {user.full_name} ({username})\n"
        f"<b>ID:</b> <code>{user.id}</code>\n"
        f"<b>Profil:</b> tg://user?id={user.id}\n\n"
        f"<b>Fan:</b> {d['fan']}\n"
        f"<b>Mavzu:</b> {d['mavzu']}\n"
        f"<b>Slaydlar:</b> {d['slayd']} ta\n"
        f"<b>Til:</b> {d['til']}\n"
        f"<b>Muddat:</b> {d['muddat']}\n"
        f"<b>Narx:</b> {narx}"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Qabul qilish", callback_data=f"accept_{user.id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user.id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=ADMIN_ID, text=xabar, parse_mode="HTML", reply_markup=reply_markup
    )

    await update.message.reply_text(
        "Buyurtmangiz adminga yuborildi! Tez orada ko'rib chiqib, siz bilan bog'lanishadi.",
        reply_markup=ReplyKeyboardMarkup(ASOSIY_MENYU, resize_keyboard=True),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data
    parts = data.split("_")
    action = parts[0]
    user_id = int(parts[1])

    if action == "accept":
        ready_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ Tayyor (To'lovni so'rash)", callback_data=f"ready_{user_id}")]
        ])
        await query.edit_message_text(
            text=query.message.text + "\n\n<b>Status:</b> ✅ Qabul qilindi (Bajarilmoqda)",
            parse_mode="HTML",
            reply_markup=ready_keyboard
        )
        await context.bot.send_message(
            chat_id=user_id,
            text="Sizning buyurtmangiz qabul qilindi va ustida ish boshlandi! 👨‍💻 Tez orada tayyor bo'ladi."
        )

    elif action == "reject":
        await query.edit_message_text(
            text=query.message.text + "\n\n<b>Status:</b> ❌ Rad etildi",
            parse_mode="HTML"
        )
        await context.bot.send_message(
            chat_id=user_id,
            text="Afsuski, sizning buyurtmangiz rad etildi."
        )

    elif action == "ready":
        await query.edit_message_text(
            text=query.message.text + "\n\n<b>Status:</b> 💰 To'lov kutilmoqda",
            parse_mode="HTML"
        )
        context.user_data[f"waiting_payment_{user_id}"] = True
        
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 <b>Prezentatsiyangiz tayyor!</b>\n\n"
                "Uni olish uchun quyidagi karta raqamiga to'lovni amalga oshiring:\n\n"
                f"💳 <b>Karta:</b> <code>{KARTA_RAQAMI}</code>\n\n"
                "To'lovni qilgandan so'ng <b>chek (kvitansiya) rasmini</b> shu yerga yuboring!"
            ),
            parse_mode="HTML"
        )

    elif action == "approvepay":
        await query.edit_message_text(
            text=query.message.text + "\n\n<b>Status:</b> ✅ To'lov tasdiqlandi. Fayl yuborilishi kutilmoqda.",
            parse_mode="HTML"
        )
        context.user_data[f"admin_sending_file_to"] = user_id
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="Endi tayyor prezentatsiya faylini (.pptx yoki hujjat) shu yerga yuboring. Men uni mijozga avtomatik yuboraman."
        )
        await context.bot.send_message(
            chat_id=user_id,
            text="To'lovingiz tasdiqlandi! Admin tez orada faylni yuboradi 📂."
        )


async def handle_photo_or_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    target_user_id = context.user_data.get("admin_sending_file_to")

    if user_id == ADMIN_ID and target_user_id:
        if update.message.document:
            await context.bot.send_document(chat_id=target_user_id, document=update.message.document.file_id, caption="Mana sizning tayyor prezentatsiyangiz! Xaridingiz uchun rahmat 😊")
        elif update.message.photo:
            await context.bot.send_photo(chat_id=target_user_id, photo=update.message.photo[-1].file_id, caption="Mana sizning tayyor prezentatsiyangiz!")
        
        context.user_data.pop("admin_sending_file_to", None)
        await update.message.reply_text("Fayl mijozga muvaffaqiyatli yuborildi! ✅")
        return

    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id

        if photo_file_id in ISHLATILGAN_CHEKLAR:
            await update.message.reply_text("❌ Bu chek oldindan ishlatilgan yoki tizimga yuborilgan! Iltimos, haqiqiy yangi chekni yuboring.")
            return

        ISHLATILGAN_CHEKLAR.add(photo_file_id)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ To'lovni tasdiqlash", callback_data=f"approvepay_{user_id}")]
        ])
        
        user = update.effective_user
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file_id,
            caption=(
                f"💳 <b>Yangi to'lov cheki keldi!</b>\n"
                f"Mijoz: {user.full_name} (<code>{user.id}</code>)\n"
                f"Karta: {KARTA_RAQAMI}\n\n"
                "Iltimos, kartangizga pul tushganini tekshiring va tasdiqlang."
            ),
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        await update.message.reply_text("Chekingiz adminga yuborildi! 🕒 Tekshirilmoqda, iltimos biroz kuting.")


async def not_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Iltimos, matn yoki kerakli ma'lumotni yuboring.")
    return update.message.chat.id


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Buyurtma bekor qilindi. Qayta boshlash uchun /start yozing.",
        reply_markup=ReplyKeyboardMarkup(ASOSIY_MENYU, resize_keyboard=True),
    )
    return ConversationHandler.END


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Sizning ID raqamingiz: <code>{update.effective_user.id}</code>", parse_mode="HTML")


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    text_only = filters.TEXT & ~filters.COMMAND
    not_text = ~filters.TEXT & ~filters.COMMAND

    conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📋 Prezentatsiya buyurtma berish$"), buyurtma_boshlash),
            MessageHandler(filters.Regex("^👨‍💻 Adminga murojaat$"), adminga_murojaat_boshlash),
        ],
        states={
            ADMINGA_YOZISH: [MessageHandler(text_only, adminga_xabar_jonatish)],
            FAN: [MessageHandler(text_only, fan), MessageHandler(not_text, not_text_handler)],
            MAVZU: [MessageHandler(text_only, mavzu), MessageHandler(not_text, not_text_handler)],
            SLAYD: [MessageHandler(text_only, slayd), MessageHandler(not_text, not_text_handler)],
            TIL: [MessageHandler(text_only, til), MessageHandler(not_text, not_text_handler)],
            MUDDAT: [MessageHandler(text_only, muddat), MessageHandler(not_text, not_text_handler)],
            TASDIQ: [MessageHandler(text_only, tasdiq), MessageHandler(not_text, not_text_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CallbackQueryHandler(admin_callback))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_photo_or_document))

    print("Bot muvaffaqiyatli ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
