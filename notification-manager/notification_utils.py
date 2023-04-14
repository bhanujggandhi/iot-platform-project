import smtplib
import ssl
from email.message import EmailMessage
from decouple import config
import time

SENDER_EMAIL = config("NOTIFICATION_SENDER_EMAIL")
SENDER_PASSWORD = config("NOTIFICATION_SENDER_PASSWORD")

class Notification:
    def __init__(self):
        try:
            self.smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            self.x = self.smtp.login(SENDER_EMAIL, SENDER_PASSWORD)

        except Exception as e:
            print(e)
            print("Unable to login Email.")

    # for ending email
    def notify(self, receiver_email, subject, body):
        time.sleep(1)
        em = EmailMessage()
        em["From"] = SENDER_EMAIL
        em["To"] = receiver_email
        em["Subject"] = subject
        em.set_content(body)

        try:
            r = self.smtp.sendmail(SENDER_EMAIL, receiver_email, em.as_string())
            print(f"Email Sent to : {receiver_email} with subject : {subject}")

        except Exception as e:
            print(e)
            print("Unable to send Email.")


# sample driver code
if __name__ == "__main__":
    receiver_email = 'ias2023.g1@gmail.com'
    subject = 'Test'
    body = 'Test Body'

    notification = Notification()
    notification.notify(receiver_email, subject, body)