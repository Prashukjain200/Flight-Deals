import smtplib
from twilio.rest import Client

TWILIO_SID = "AC36bcca6aae045996354b44230cb39a72"
TWILIO_AUTH_TOKEN = "232b5a86bb4e385898b9b17126f44b28"
TWILIO_VIRTUAL_NUMBER = "+13203372358"
TWILIO_VERIFIED_NUMBER = "+91"
MAIL_PROVIDER_SMTP_ADDRESS = "smtp.gmail.com"
MY_EMAIL = "jain86895@gmail.com"
MY_PASSWORD = "Prashukjain"

class NotificationManager:

    def __init__(self, number):
        self.client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        self.number = number

    def send_sms(self, message):
        message = self.client.messages.create(
            body=message,
            from_=TWILIO_VIRTUAL_NUMBER,
            to=TWILIO_VERIFIED_NUMBER + str(self.number),
        )
        print(message.sid)

    def send_emails(self, emails, message, google_flight_link):
        with smtplib.SMTP(MAIL_PROVIDER_SMTP_ADDRESS) as connection:
            connection.starttls()
            connection.login(MY_EMAIL, MY_PASSWORD)
            for email in emails:
                connection.sendmail(
                    from_addr=MY_EMAIL,
                    to_addrs=email,
                    msg=f"Subject:New Low Price Flight!\n\n{message}\n{google_flight_link}".encode('utf-8')
                )