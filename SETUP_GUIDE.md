# 📱 Telegram Earning Bot — সম্পূর্ণ গাইড

## ✅ বটে কী কী আছে?
- 📺 Ad দেখে আয় (দিনে ১০টি)
- ✅ Daily Task (Channel Join)
- 👥 Referral System (প্রতিজনে ৫ টাকা)
- 💰 Balance ও Withdraw (Bkash/Nagad)
- 🔧 Admin Panel (/admin command)
- 📢 Withdrawal Notification

---

## 🛠️ STEP 1: Bot Token নিন

1. Telegram-এ [@BotFather](https://t.me/BotFather) তে যান
2. `/newbot` লিখুন
3. বটের নাম দিন (যেমন: My Earning Bot)
4. Username দিন (যেমন: myearningbot)
5. **Token** কপি করুন (এরকম দেখতে: `123456:ABCdef...`)

---

## 🛠️ STEP 2: Admin ID নিন

1. Telegram-এ [@userinfobot](https://t.me/userinfobot) তে `/start` দিন
2. আপনার **User ID** কপি করুন (সংখ্যা)

---

## 🛠️ STEP 3: Render.com-এ Deploy করুন (Free)

### প্রথমে GitHub-এ Upload করুন:

1. [github.com](https://github.com) এ Account বানান
2. New Repository তৈরি করুন (নাম: `earning-bot`)
3. এই ফোল্ডারের সব ফাইল Upload করুন:
   - `bot.py`
   - `web_server.py`
   - `requirements.txt`
   - `start.sh`

### তারপর Render.com:

1. [render.com](https://render.com) এ যান → Sign up with GitHub
2. **New** → **Web Service** ক্লিক করুন
3. আপনার Repository সিলেক্ট করুন
4. এই Settings দিন:

```
Name: earning-bot
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: bash start.sh
```

5. **Environment Variables** এ Add করুন:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | আপনার BotFather Token |
| `ADMIN_ID` | আপনার Telegram User ID |
| `BOT_USERNAME` | বটের username (@ ছাড়া) |
| `WEB_APP_URL` | Render-এ Deploy হলে URL পাবেন |
| `AD_REWARD` | 2 |
| `TASK_REWARD` | 10 |

6. **Create Web Service** ক্লিক করুন
7. Deploy হতে ৫-১০ মিনিট লাগবে

---

## 🛠️ STEP 4: Ad Network Setup (Monetag)

1. [monetag.com](https://monetag.com) এ Account বানান
2. Publisher হিসেবে Register করুন
3. **New Zone** → **Popunder** বা **Banner** সিলেক্ট করুন
4. Ad Code পাবেন — সেটি `web_server.py` ফাইলে এখানে বসান:

```python
<!-- MONETAG AD CODE START -->
# এখানে আপনার Monetag Script paste করুন
<!-- MONETAG AD CODE END -->
```

5. Code বসিয়ে GitHub-এ Update করুন
6. Render Auto-redeploy করবে

---

## 🛠️ STEP 5: Channel Setup

`bot.py` ফাইলে এই লাইন আপডেট করুন:

```python
[InlineKeyboardButton("📢 Channel Join করুন", url="https://t.me/YOUR_CHANNEL")],
```

`YOUR_CHANNEL` এর জায়গায় আপনার চ্যানেলের নাম দিন।

---

## 📱 Admin Commands

বটে এই Commands ব্যবহার করুন:

| Command | কাজ |
|---------|-----|
| `/admin` | Admin Panel দেখুন |
| `/approve 1` | Withdrawal #1 Approve করুন |

---

## 💡 Withdrawal Approve করবেন কিভাবে?

1. ইউজার Withdraw Request করলে **আপনার কাছে Notification আসবে**
2. Notification-এ Withdrawal ID দেখবেন
3. বটে `/approve <ID>` লিখুন
4. ইউজার Automatically Notification পাবে

---

## 💰 আয়ের হিসাব

| কাজ | আয় |
|-----|-----|
| ১টি Ad দেখা | ২ টাকা |
| Daily Task | ১০ টাকা |
| ১ জন Refer | ৫ টাকা |
| দৈনিক সর্বোচ্চ (Ad) | ২০ টাকা |
| Daily Task যোগে | ৩০ টাকা/দিন |

---

## ❓ সমস্যা হলে কী করবেন?

- Render Dashboard → **Logs** দেখুন
- Error দেখলে: BOT_TOKEN সঠিক আছে কিনা চেক করুন
- বট Reply না করলে: Render Service Restart করুন

---

*এই বট সম্পূর্ণ আপনার নিজের। যেকোনো সমস্যায় বটের Log চেক করুন।*
