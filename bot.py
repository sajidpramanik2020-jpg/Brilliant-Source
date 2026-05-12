import os
import sqlite3
import logging
from datetime import datetime, date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://brilliant-source.onrender.com")
MIN_WITHDRAW = 50
AD_REWARD = int(os.environ.get("AD_REWARD", "2"))
TASK_REWARD = int(os.environ.get("TASK_REWARD", "10"))
MAX_ADS_PER_DAY = 10

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect("earning_bot.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        balance REAL DEFAULT 0,
        total_earned REAL DEFAULT 0,
        referred_by INTEGER,
        joined_at TEXT,
        is_banned INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS daily_stats (
        user_id INTEGER,
        stat_date TEXT,
        ads_watched INTEGER DEFAULT 0,
        task_done INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, stat_date))""")
    c.execute("""CREATE TABLE IF NOT EXISTS withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        method TEXT,
        number TEXT,
        status TEXT DEFAULT 'pending',
        requested_at TEXT,
        processed_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS referrals (
        referrer_id INTEGER,
        referred_id INTEGER,
        joined_at TEXT,
        PRIMARY KEY (referred_id))""")
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("earning_bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def register_user(user_id, username, full_name, referred_by=None):
    conn = sqlite3.connect("earning_bot.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, username, full_name, referred_by, joined_at) VALUES (?,?,?,?,?)",
            (user_id, username, full_name, referred_by, datetime.now().isoformat()))
        if referred_by:
            c.execute("INSERT OR IGNORE INTO referrals (referrer_id, referred_id, joined_at) VALUES (?,?,?)",
                (referred_by, user_id, datetime.now().isoformat()))
            c.execute("UPDATE users SET balance=balance+5, total_earned=total_earned+5 WHERE user_id=?", (referred_by,))
        conn.commit()
    conn.close()

def get_today_stats(user_id):
    conn = sqlite3.connect("earning_bot.db")
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("SELECT ads_watched, task_done FROM daily_stats WHERE user_id=? AND stat_date=?", (user_id, today))
    row = c.fetchone()
    conn.close()
    return row if row else (0, 0)

def add_ad_watch(user_id):
    conn = sqlite3.connect("earning_bot.db")
    c = conn.cursor()
    today = date.today().isoformat()
    ads, task = get_today_stats(user_id)
    if ads >= MAX_ADS_PER_DAY:
        conn.close()
        return False
    c.execute("INSERT OR REPLACE INTO daily_stats (user_id, stat_date, ads_watched, task_done) VALUES (?,?,?,?)",
        (user_id, today, ads + 1, task))
    c.execute("UPDATE users SET balance=balance+?, total_earned=total_earned+? WHERE user_id=?",
        (AD_REWARD, AD_REWARD, user_id))
    conn.commit()
    conn.close()
    return True

def complete_daily_task(user_id):
    conn = sqlite3.connect("earning_bot.db")
    c = conn.cursor()
    today = date.today().isoformat()
    ads, task = get_today_stats(user_id)
    if task >= 1:
        conn.close()
        return False
    c.execute("INSERT OR REPLACE INTO daily_stats (user_id, stat_date, ads_watched, task_done) VALUES (?,?,?,?)",
        (user_id, today, ads, 1))
    c.execute("UPDATE users SET balance=balance+?, total_earned=total_earned+? WHERE user_id=?",
        (TASK_REWARD, TASK_REWARD, user_id))
    conn.commit()
    conn.close()
    return True

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📺 Ads দেখুন & আয় করুন", callback_data="watch_ad")],
        [InlineKeyboardButton("✅ Daily Task", callback_data="daily_task"),
         InlineKeyboardButton("👥 Refer করুন", callback_data="refer")],
        [InlineKeyboardButton("💰 Balance & Withdraw", callback_data="balance")],
        [InlineKeyboardButton("📊 আমার Stats", callback_data="stats")],
    ])

def back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 মেনুতে ফিরুন", callback_data="menu")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referred_by = None
    if context.args:
        try:
            referred_by = int(context.args[0])
            if referred_by == user.id:
                referred_by = None
        except:
            pass
    register_user(user.id, user.username or "", user.full_name, referred_by)
    await update.message.reply_text(
        f"🌟 *স্বাগতম, {user.first_name}!*\n\n"
        "আপনি আমাদের Earning Bot-এ যোগ দিয়েছেন!\n\n"
        "💡 *কিভাবে আয় করবেন:*\n"
        f"📺 Ads দেখুন → প্রতিটিতে {AD_REWARD} টাকা\n"
        f"✅ Daily Task → প্রতিদিন {TASK_REWARD} টাকা\n"
        f"👥 রেফার করুন → প্রতিজনে ৫ টাকা\n\n"
        f"💸 *মিনিমাম Withdraw:* {MIN_WITHDRAW} টাকা\n"
        "🏦 Bkash / Nagad-এ পেমেন্ট পাবেন\n\n"
        "নিচের মেনু থেকে শুরু করুন 👇",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if data == "menu":
        await query.edit_message_text(
            f"🏠 *মেইন মেনু*\n\nস্বাগতম, {user.first_name}!",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    elif data == "watch_ad":
        ads_today, _ = get_today_stats(user.id)
        remaining = MAX_ADS_PER_DAY - ads_today
        if remaining <= 0:
            await query.edit_message_text(
                "⏰ *আজকের Ad সীমা শেষ!*\n\nকাল আবার আসুন! 🌅",
                parse_mode="Markdown", reply_markup=back_keyboard())
            return
        ad_url = f"{WEB_APP_URL}/ad?user={user.id}"
        await query.edit_message_text(
            f"📺 *Ad দেখুন*\n\nআজ বাকি: *{remaining}টি* Ad\nপ্রতিটি Ad: *{AD_REWARD} টাকা*\n\n"
            "👇 নিচের বাটনে ক্লিক করে Ad দেখুন,\nতারপর ✅ বাটন চাপুন।",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📺 Ad দেখুন", url=ad_url)],
                [InlineKeyboardButton("✅ Ad দেখা হয়েছে", callback_data="confirm_ad")],
                [InlineKeyboardButton("🔙 মেনুতে ফিরুন", callback_data="menu")],
            ])
        )

    elif data == "confirm_ad":
        success = add_ad_watch(user.id)
        if success:
            ads_today, _ = get_today_stats(user.id)
            remaining = MAX_ADS_PER_DAY - ads_today
            await query.edit_message_text(
                f"✅ *Ad দেখার জন্য ধন্যবাদ!*\n\n💰 পেয়েছেন: *{AD_REWARD} টাকা*\nআজ বাকি: *{remaining}টি* Ad",
                parse_mode="Markdown", reply_markup=back_keyboard())
        else:
            await query.edit_message_text("⏰ আজকের Ad সীমা শেষ!", reply_markup=back_keyboard())

    elif data == "daily_task":
        _, task_done = get_today_stats(user.id)
        if task_done:
            await query.edit_message_text(
                "✅ *আজকের Daily Task সম্পন্ন!*\n\nকাল আবার আসুন! 🌅",
                parse_mode="Markdown", reply_markup=back_keyboard())
            return
        await query.edit_message_text(
            f"✅ *Daily Task*\n\nReward: *{TASK_REWARD} টাকা*\n\n"
            "📌 আজকের Task:\nআমাদের Telegram Channel Join করুন!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Channel Join করুন", url="https://t.me/your_channel")],
                [InlineKeyboardButton("✅ Join করেছি, Reward নিন!", callback_data="confirm_task")],
                [InlineKeyboardButton("🔙 মেনুতে ফিরুন", callback_data="menu")],
            ])
        )

    elif data == "confirm_task":
        success = complete_daily_task(user.id)
        if success:
            await query.edit_message_text(
                f"🎉 *Daily Task সম্পন্ন!*\n\n💰 পেয়েছেন: *{TASK_REWARD} টাকা*",
                parse_mode="Markdown", reply_markup=back_keyboard())
        else:
            await query.edit_message_text("✅ আজকের Task আগেই সম্পন্ন হয়েছে!", reply_markup=back_keyboard())

    elif data == "refer":
        ref_link = f"https://t.me/{context.bot.username}?start={user.id}"
        conn = sqlite3.connect("earning_bot.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id=?", (user.id,))
        ref_count = c.fetchone()[0]
        conn.close()
        await query.edit_message_text(
            f"👥 *আপনার Referral লিংক*\n\n`{ref_link}`\n\n"
            f"📊 মোট Refer: *{ref_count} জন*\n💰 প্রতি Refer: *৫ টাকা*",
            parse_mode="Markdown", reply_markup=back_keyboard())

    elif data == "balance":
        row = get_user(user.id)
        balance = row[3] if row else 0
        total = row[4] if row else 0
        await query.edit_message_text(
            f"💰 *আপনার Balance*\n\n💵 বর্তমান: *{balance:.0f} টাকা*\n📈 মোট আয়: *{total:.0f} টাকা*\n\n"
            f"💸 Minimum Withdraw: *{MIN_WITHDRAW} টাকা*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💸 Withdraw করুন", callback_data="withdraw")],
                [InlineKeyboardButton("🔙 মেনুতে ফিরুন", callback_data="menu")],
            ])
        )

    elif data == "withdraw":
        row = get_user(user.id)
        balance = row[3] if row else 0
        if balance < MIN_WITHDRAW:
            await query.edit_message_text(
                f"❌ *Withdraw করা যাচ্ছে না*\n\nBalance: *{balance:.0f} টাকা*\nদরকার: *{MIN_WITHDRAW} টাকা*\n\n"
                f"আরো *{MIN_WITHDRAW - balance:.0f} টাকা* আয় করুন।",
                parse_mode="Markdown", reply_markup=back_keyboard())
            return
        await query.edit_message_text(
            f"💸 *Withdraw*\n\nBalance: *{balance:.0f} টাকা*\n\nপেমেন্ট মেথড সিলেক্ট করুন:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📱 Bkash", callback_data="wd_bkash"),
                 InlineKeyboardButton("📱 Nagad", callback_data="wd_nagad")],
                [InlineKeyboardButton("🔙 মেনুতে ফিরুন", callback_data="menu")],
            ])
        )

    elif data in ["wd_bkash", "wd_nagad"]:
        method = "Bkash" if data == "wd_bkash" else "Nagad"
        context.user_data["withdraw_method"] = method
        context.user_data["awaiting_withdraw"] = True
        await query.edit_message_text(
            f"📱 *{method} Withdraw*\n\nআপনার {method} নম্বর লিখুন:\n(যেমন: 01XXXXXXXXX)",
            parse_mode="Markdown")

    elif data == "stats":
        row = get_user(user.id)
        balance = row[3] if row else 0
        total = row[4] if row else 0
        ads_today, task_today = get_today_stats(user.id)
        conn = sqlite3.connect("earning_bot.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id=?", (user.id,))
        ref_count = c.fetchone()[0]
        conn.close()
        await query.edit_message_text(
            f"📊 *আপনার Stats*\n\n💵 Balance: *{balance:.0f} টাকা*\n📈 মোট আয়: *{total:.0f} টাকা*\n\n"
            f"📅 *আজকের রিপোর্ট:*\n📺 Ad: *{ads_today}/{MAX_ADS_PER_DAY}টি*\n"
            f"✅ Daily Task: *{'সম্পন্ন ✅' if task_today else 'বাকি ❌'}*\n\n"
            f"👥 মোট Refer: *{ref_count} জন*",
            parse_mode="Markdown", reply_markup=back_keyboard())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.user_data.get("awaiting_withdraw"):
        number = update.message.text.strip()
        method = context.user_data.get("withdraw_method", "Bkash")
        row = get_user(user.id)
        balance = row[3] if row else 0
        if balance < MIN_WITHDRAW:
            await update.message.reply_text("❌ Balance কম আছে।")
            context.user_data.clear()
            return
        conn = sqlite3.connect("earning_bot.db")
        c = conn.cursor()
        c.execute("INSERT INTO withdrawals (user_id, amount, method, number, requested_at) VALUES (?,?,?,?,?)",
            (user.id, balance, method, number, datetime.now().isoformat()))
        c.execute("UPDATE users SET balance=0 WHERE user_id=?", (user.id,))
        conn.commit()
        conn.close()
        context.user_data.clear()
        try:
            await context.bot.send_message(ADMIN_ID,
                f"💸 *নতুন Withdraw Request!*\n\n👤 {user.full_name}\n🆔 `{user.id}`\n"
                f"💰 *{balance:.0f} টাকা*\n📱 {method}: `{number}`",
                parse_mode="Markdown")
        except:
            pass
        await update.message.reply_text(
            f"✅ *Withdraw Request সফল!*\n\n💰 *{balance:.0f} টাকা*\n📱 {method}: `{number}`\n\n"
            "⏳ ২৪-৪৮ ঘণ্টার মধ্যে পেমেন্ট পাবেন। 🙏",
            parse_mode="Markdown", reply_markup=main_menu_keyboard())

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect("earning_bot.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM withdrawals WHERE status='pending'")
    pending_wd = c.fetchone()[0]
    conn.close()
    await update.message.reply_text(
        f"🔧 *Admin Panel*\n\n👥 Total Users: *{total_users}*\n⏳ Pending Withdrawals: *{pending_wd}*",
        parse_mode="Markdown")

async def approve_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /approve <id>")
        return
    wd_id = context.args[0]
    conn = sqlite3.connect("earning_bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM withdrawals WHERE id=?", (wd_id,))
    wd = c.fetchone()
    if not wd:
        await update.message.reply_text("❌ পাওয়া যায়নি।")
        conn.close()
        return
    c.execute("UPDATE withdrawals SET status='approved', processed_at=? WHERE id=?",
        (datetime.now().isoformat(), wd_id))
    conn.commit()
    conn.close()
    try:
        await context.bot.send_message(wd[1],
            f"🎉 *Withdrawal Approved!*\n\n💰 *{wd[2]:.0f} টাকা*\nপেমেন্ট পাঠানো হয়েছে। 🙏",
            parse_mode="Markdown")
    except:
        pass
    await update.message.reply_text(f"✅ Withdrawal #{wd_id} Approved!")

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("approve", approve_withdrawal))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    logger.info("Bot চালু হচ্ছে...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
        
