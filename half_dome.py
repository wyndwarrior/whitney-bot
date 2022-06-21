import json
import traceback
import requests
import time
import os

from fbchat import Client
from fbchat.models import *
from datetime import datetime
import pytz

tz = pytz.timezone('America/Los_Angeles') 
client = Client(os.environ['FBEMAIL'] , os.environ["FBPASSWORD"])

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
}

permit_key = '44585917'

prev_message = None

if os.path.exists("prev_message_hd.txt"):
    with open("prev_message_hd.txt", "r") as f:
        prev_message = f.read()

while True:
    now = datetime.now(tz)
    try:
        all_found = []

        for url in [
            'https://www.recreation.gov/api/permitinyo/445859/availability?start_date=2022-07-01&end_date=2022-07-31&commercial_acct=false',
            "https://www.recreation.gov/api/permitinyo/445859/availability?start_date=2022-06-01&end_date=2022-06-30&commercial_acct=false",
        ]:
            resp = requests.get(url=url, headers=headers)
            data = resp.json()

            availability = data['payload']
            for date, date_avail in availability.items():
                if permit_key in date_avail and date_avail[permit_key]['remaining'] > 0:
                    all_found.append((f"{date}: {date_avail[permit_key]['remaining']} permit(s) available"))

        message = "Half Dome bot:\n" + "\n".join(all_found) + "\n\nhttps://www.recreation.gov/permits/445859/registration/detailed-availability to book\n\n"

        now_str = now.strftime("%H:%M:%S")

        print(message + now_str)

        if message != prev_message:
            client.send(Message(text=message + now_str), thread_id=os.environ['FBTHREAD'], thread_type=ThreadType.GROUP)

            prev_message = message
            with open("prev_message.txt", "w") as f:
                f.write(message)
    except:
        try:
            client.send(Message(text=traceback.format_exc()), thread_id=os.environ['FBTHREAD'], thread_type=ThreadType.GROUP)
        except:
            pass
    if abs((now.replace(hour=7, minute=0) - now).total_seconds()) < 60*30:
        print(abs((now.replace(hour=7, minute=0) - now).total_seconds()))
        time.sleep(10)
    else:
        time.sleep(60)
