import logging
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running ✅", 200

def _run():
    # FIX: debug=False, use_reloader=False required when running in a thread
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def keep_alive():
    t = Thread(target=_run, daemon=True)  # FIX: daemon=True so it doesn't block shutdown
    t.start()
    logging.info(" >> Keep-alive server started on port 5000")
