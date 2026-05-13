#!/bin/bash
pip install python-telegram-bot==20.3 httpx==0.24.1 httpcore==0.17.3 flask gunicorn
gunicorn web_server:app --bind 0.0.0.0:$PORT --daemon
python bot.py
