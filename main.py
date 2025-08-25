import os
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# ==========================
# CONFIG
# ==========================
TOKEN = os.environ["BOT_TOKEN"]

# user_data = {user_id: {"balance": 0, "withdrawable": 0}}
user_data = {}
captcha_answers = {}
INVITE_REWARD = 100
WITHDRAW_LIMIT = 888

# ==========================
# HELPERS
# ==========================
def generate_captcha_text(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_captcha_image(text):
    img = Image.new('RGB', (150, 60), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    d.text((10, 10), text, fill=(0, 0, 0), font=font)
    bio = BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio

def get_balances(user_id):
    data = user_data.setdefault(user_id, {"balance": 0, "withdrawable": 0})
    return data["balance"], data["withdrawable"]

# ==========================
# COMMANDS
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data.setdefault(user.id, {"balance": 0, "withdrawable": 0})
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        "💰 Check balance: /balance\n"
        "🧩 Solve captcha: /captcha2earn\n"
        "🎲 Play Dice: /dice\n"
        "🎰 Scatter Spin: /scatterspin\n"
        "💵 Withdraw: /withdraw\n"
        "📩 Invite friends: /invite\n\n"
        "📌 Note: Only game winnings add to your withdrawable balance!"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bal, withdrawable = get_balances(user.id)
    await update.message.reply_text(
        f"⚖️ Playable Balance: ₱{bal}\n"
        f"💵 Withdrawable Balance: ₱{withdrawable}\n\n"
        "📌 You can withdraw once withdrawable ≥ ₱888"
    )

# ==========================
# CAPTCHA
# ==========================
async def captcha2earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    captcha_text = generate_captcha_text()
    captcha_answers[user.id] = captcha_text
    img = generate_captcha_image(captcha_text)
    await update.message.reply_photo(photo=InputFile(img), caption="🧩 Type the letters/numbers to earn ₱ (playable only)!")

async def check_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in captcha_answers:
        answer = captcha_answers[user.id]
        if update.message.text.strip().upper() == answer:
            reward = random.randint(10, 50)
            user_data.setdefault(user.id, {"balance": 0, "withdrawable": 0})
            user_data[user.id]["balance"] += reward
            await update.message.reply_text(
                f"✅ Correct! You earned ₱{reward} (Playable only).\n"
                f"🎮 Play games to convert into withdrawable balance!"
            )
        else:
            await update.message.reply_text("❌ Wrong captcha! Try /captcha2earn again.")
        del captcha_answers[user.id]

# ==========================
# DICE GAME
# ==========================
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎲 Enter your bet amount for Dice:")
    return 1

async def dice_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        bet = int(update.message.text)
        bal, withdrawable = get_balances(user.id)
        if bet > bal:
            await update.message.reply_text("🚫 Not enough balance.")
            return ConversationHandler.END

        user_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        if user_roll > bot_roll:
            user_data[user.id]["balance"] += bet
            user_data[user.id]["withdrawable"] += bet
            await update.message.reply_text(
                f"🎲 You rolled {user_roll}, bot rolled {bot_roll}.\n"
                f"🎉 You won ₱{bet}! (Added to both balances)\n"
                f"New: Playable ₱{user_data[user.id]['balance']}, Withdrawable ₱{user_data[user.id]['withdrawable']}"
            )
        else:
            user_data[user.id]["balance"] -= bet
            await update.message.reply_text(
                f"🎲 You rolled {user_roll}, bot rolled {bot_roll}.\n"
                f"😢 You lost ₱{bet}. (Deducted from playable only)\n"
                f"New: Playable ₱{user_data[user.id]['balance']}, Withdrawable ₱{user_data[user.id]['withdrawable']}"
            )
    except:
        await update.message.reply_text("❌ Enter a valid number.")
    return ConversationHandler.END

# ==========================
# SCATTER SPIN
# ==========================
async def scatterspin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎰 Scatter Spin Rules:\n"
        "➡️ 3 same symbols = Jackpot (x3 bet)\n"
        "➡️ 2 same symbols = Small win (+bet)\n"
        "➡️ No match = Lose bet\n\n"
        "Enter your bet amount:"
    )
    return 1

async def scatterspin_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        bet = int(update.message.text)
        bal, withdrawable = get_balances(user.id)
        if bet > bal:
            await update.message.reply_text("🚫 Not enough balance.")
            return ConversationHandler.END

        symbols = ["🍒", "7️⃣", "⭐", "💎"]
        spin = [random.choice(symbols) for _ in range(3)]
        result = " ".join(spin)

        if len(set(spin)) == 1:  # 3 match
            win = bet * 3
            user_data[user.id]["balance"] += win
            user_data[user.id]["withdrawable"] += win
            msg = f"{result}\n🎉 JACKPOT! You won ₱{win}!"
        elif len(set(spin)) == 2:  # 2 match
            win = bet
            user_data[user.id]["balance"] += win
            user_data[user.id]["withdrawable"] += win
            msg = f"{result}\n🎊 Nice! You matched 2 symbols and won ₱{win}!"
        else:
            user_data[user.id]["balance"] -= bet
            msg = f"{result}\n😢 No match. You lost ₱{bet}."

        await update.message.reply_text(
            f"{msg}\n\n"
            f"Playable: ₱{user_data[user.id]['balance']} | Withdrawable: ₱{user_data[user.id]['withdrawable']}"
        )
    except:
        await update.message.reply_text("❌ Enter a valid number.")
    return ConversationHandler.END

# ==========================
# WITHDRAW
# ==========================
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bal, withdrawable = get_balances(user.id)

    if withdrawable < WITHDRAW_LIMIT:
        await update.message.reply_text(
            f"🚫 Minimum withdrawable is ₱{WITHDRAW_LIMIT}.\n"
            f"💵 Your withdrawable: ₱{withdrawable}"
        )
    else:
        await update.message.reply_text(
            f"💵 Withdrawal request started!\n"
            f"Amount: ₱{withdrawable}\n"
            f"Please send your Full Name + GCash number."
        )
        user_data[user.id]["withdrawable"] = 0  # reset withdrawable only

# ==========================
# INVITE
# ==========================
async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bal, withdrawable = get_balances(user.id)
    user_data[user.id]["balance"] += INVITE_REWARD
    await update.message.reply_text(
        f"📩 Invite bonus! You earned ₱{INVITE_REWARD} (Playable only).\n"
        f"New balance: ₱{user_data[user.id]['balance']}"
    )

# ==========================
# MAIN
# ==========================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("captcha2earn", captcha2earn))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("invite", invite))

    dice_conv = ConversationHandler(
        entry_points=[CommandHandler("dice", dice)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, dice_bet)]},
        fallbacks=[]
    )
    scatter_conv = ConversationHandler(
        entry_points=[CommandHandler("scatterspin", scatterspin)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, scatterspin_bet)]},
        fallbacks=[]
    )

    app.add_handler(dice_conv)
    app.add_handler(scatter_conv)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_captcha))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
