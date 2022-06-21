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

print("Own id: {}".format(client.uid))


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
}

prev_message = None
if os.path.exists("prev_message.txt"):
    with open("prev_message.txt", "r") as f:
        prev_message = f.read()

while True:

    try:

        all_found = []

        for name, url in [
            ("overnight", "https://www.recreation.gov/api/permits/233260/divisions/166/availability?start_date=2022-01-01T00:00:00.000Z&end_date=2023-04-30T00:00:00.000Z&commercial_acct=false"),
            # ("day permit", "https://www.recreation.gov/api/permits/233260/divisions/406/availability?start_date=2022-01-01T00:00:00.000Z&end_date=2023-04-30T00:00:00.000Z&commercial_acct=false")
            ]:

            resp = requests.get(url=url, headers=headers)
            data = resp.json()

            next_available = data['payload']['next_available_date']
            availability = data['payload']['date_availability']
            availability_dates = list(availability.keys())

            if next_available in availability_dates:
                idx = availability_dates.index(next_available)
                for k in availability_dates[idx:]:
                    if availability[k]['remaining'] > 0:
                        all_found.append((f"{name}: {k}, {availability[k]['remaining']} permit(s) available"))

        message = "Whitney bot:\n" + "\n".join(all_found) + "\n\nhttps://www.recreation.gov/permits/233260 to book\n\n"

        now = datetime.now(tz)
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

    time.sleep(60)
