#!/bin/bash
# বট এবং Web Server একসাথে চালু করুন
echo "🚀 Earning Bot চালু হচ্ছে..."
gunicorn web_server:app --bind 0.0.0.0:$PORT --daemon
python bot.py
