"""
Ad Web Server - ইউজার এই পেজে এসে Ad দেখবে
Monetag বা AdStera-র Ad Code এখানে বসাতে হবে
"""
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# ── Ad Page HTML ──────────────────────────────────────────────────────────────
AD_PAGE = """
<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ad দেখুন — Earning Bot</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }
    .card {
      background: rgba(255,255,255,0.05);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 20px;
      padding: 40px 30px;
      max-width: 420px;
      width: 90%;
      text-align: center;
    }
    .icon { font-size: 60px; margin-bottom: 15px; }
    h1 { font-size: 24px; margin-bottom: 8px; color: #a78bfa; }
    p { color: #cbd5e1; margin-bottom: 20px; line-height: 1.6; }
    .reward-badge {
      background: linear-gradient(135deg, #7c3aed, #4f46e5);
      border-radius: 50px;
      padding: 10px 25px;
      font-size: 18px;
      font-weight: bold;
      margin: 20px 0;
      display: inline-block;
    }
    /* ── AD CONTAINER ── */
    .ad-container {
      margin: 25px 0;
      min-height: 250px;
      border-radius: 12px;
      overflow: hidden;
      background: rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .timer-bar {
      width: 100%;
      height: 6px;
      background: rgba(255,255,255,0.1);
      border-radius: 3px;
      overflow: hidden;
      margin: 15px 0;
    }
    .timer-fill {
      height: 100%;
      background: linear-gradient(90deg, #7c3aed, #a78bfa);
      border-radius: 3px;
      animation: fillUp 15s linear forwards;
    }
    @keyframes fillUp { from { width: 0%; } to { width: 100%; } }
    .btn-back {
      display: inline-block;
      background: linear-gradient(135deg, #7c3aed, #4f46e5);
      color: white;
      padding: 14px 35px;
      border-radius: 50px;
      text-decoration: none;
      font-weight: bold;
      font-size: 16px;
      margin-top: 10px;
      transition: transform 0.2s;
      opacity: 0;
      pointer-events: none;
    }
    .btn-back.active { opacity: 1; pointer-events: all; }
    .countdown { font-size: 14px; color: #94a3b8; margin-top: 10px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">📺</div>
    <h1>Ad দেখুন</h1>
    <p>নিচের Ad দেখুন এবং Telegram বটে ফিরে<br>
    <strong>✅ Ad দেখা হয়েছে</strong> বাটন চাপুন।</p>

    <div class="reward-badge">💰 +{{ reward }} টাকা পাবেন</div>

    <!-- ══════════════════════════════════════════
         এখানে আপনার Monetag / AdStera Ad Code বসান
         ══════════════════════════════════════════ -->
    <div class="ad-container">
      <!-- MONETAG AD CODE START -->
      <!-- আপনার Ad Network থেকে পাওয়া script/code এখানে paste করুন -->
      <div style="color:#64748b; font-size:14px;">
        📢 Ad Loading...<br>
        <small>(আপনার Ad Code এখানে বসান)</small>
      </div>
      <!-- MONETAG AD CODE END -->
    </div>

    <div class="timer-bar">
      <div class="timer-fill"></div>
    </div>
    <div class="countdown" id="countdown">⏳ ১৫ সেকেন্ড অপেক্ষা করুন...</div>

    <br>
    <a href="https://t.me/{{ bot_username }}" class="btn-back" id="backBtn">
      ✅ Telegram-এ ফিরুন
    </a>
  </div>

  <script>
    let seconds = 15;
    const btn = document.getElementById('backBtn');
    const txt = document.getElementById('countdown');

    const timer = setInterval(() => {
      seconds--;
      if (seconds <= 0) {
        clearInterval(timer);
        btn.classList.add('active');
        txt.textContent = '✅ এখন Telegram বটে ফিরে Reward নিন!';
        txt.style.color = '#a78bfa';
      } else {
        txt.textContent = `⏳ ${seconds} সেকেন্ড অপেক্ষা করুন...`;
      }
    }, 1000);
  </script>
</body>
</html>
"""

BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot")
AD_REWARD = int(os.getenv("AD_REWARD", "2"))

@app.route("/")
def home():
    return "<h2>✅ Earning Bot Server চালু আছে!</h2>"

@app.route("/ad")
def ad_page():
    user_id = request.args.get("user", "")
    return render_template_string(
        AD_PAGE,
        user_id=user_id,
        reward=AD_REWARD,
        bot_username=BOT_USERNAME
    )

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
