import json
import requests
from twilio.rest import Client
import time
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
}


# Your Account SID from twilio.com/console
account_sid = os.environ["ACCOUNT_SID"]
auth_token  = os.environ['AUTH_TOKEN'] 
to_numbers = json.loads(os.environ['TO_NUMBERS'])

client = Client(account_sid, auth_token)

prev_message = None

if os.path.exists("prev_message.txt"):
    with open("prev_message.txt", "r") as f:
        prev_message = f.read()

while True:

    all_found = []

    for name, url in [
        ("overnight", "https://www.recreation.gov/api/permits/233260/divisions/166/availability?start_date=2022-01-01T00:00:00.000Z&end_date=2023-04-30T00:00:00.000Z&commercial_acct=false"),
        ("day permit", "https://www.recreation.gov/api/permits/233260/divisions/406/availability?start_date=2022-01-01T00:00:00.000Z&end_date=2023-04-30T00:00:00.000Z&commercial_acct=false")]:

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

    message = "Whitney bot:\n" + "\n".join(all_found) + "\n\nhttps://www.recreation.gov/permits/233260 to book "

    print(message)

    if message != prev_message:
        for to_number in to_numbers:
            client.messages.create(
                to=to_number, 
                from_=os.environ["TWILIO_NUMBER"],
                body=message)

        prev_message = message
        with open("prev_message.txt", "w") as f:
            f.write(message)

    time.sleep(60 * 5)
