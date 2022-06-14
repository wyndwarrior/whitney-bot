import json
import requests
from twilio.rest import Client
import time
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
}

permit_key = '44585917'

# Your Account SID from twilio.com/console
account_sid = os.environ["ACCOUNT_SID"]
auth_token  = os.environ['AUTH_TOKEN'] 
to_numbers = json.loads(os.environ['TO_NUMBERS_HD'])

client = Client(account_sid, auth_token)

prev_message = None

if os.path.exists("prev_message_hd.txt"):
    with open("prev_message_hd.txt", "r") as f:
        prev_message = f.read()

while True:

    all_found = []

    resp = requests.get(url="https://www.recreation.gov/api/permitinyo/445859/availability?start_date=2022-06-01&end_date=2022-06-30&commercial_acct=false", headers=headers)
    data = resp.json()

    availability = data['payload']
    for k, v in availability.items():
        if permit_key in availability and availability[permit_key]['remaining'] > 0:
            all_found.append((f"{k}: {availability[permit_key]['remaining']} permit(s) available"))

    message = "Half Dome bot:\n" + "\n".join(all_found) + "\n\nhttps://www.recreation.gov/permits/445859/registration/detailed-availability to book "

    print(message)

    if message != prev_message:
        for to_number in to_numbers:
            client.messages.create(
                to=to_number, 
                from_=os.environ["TWILIO_NUMBER"],
                body=message)

        prev_message = message
        with open("prev_message_hd.txt", "w") as f:
            f.write(message)

    time.sleep(60 * 5)
