import smtplib
import ssl
import time
from decouple import config
from email.message import EmailMessage
from logger_utils import Logger

SENDER_EMAIL = config("NOTIFICATION_SENDER_EMAIL")
SENDER_PASSWORD = config("NOTIFICATION_SENDER_PASSWORD")

SERVICE_NAME = "notification-service"

# Creating object of class Logger
logger = Logger()


class Notification:
    def __init__(self):
        try:
            self.smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            self.x = self.smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            logger.log(
                service_name=SERVICE_NAME,
                level=0,
                msg="Login successful on SMTP Server.",
            )

        except Exception as e:
            print(e)
            print("Unable to login Email.")
            logger.log(
                service_name=SERVICE_NAME, level=4, msg="Login failure on SMTP Server."
            )

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
            msg = f"Email Sent to : {receiver_email} with subject : {subject}"
            print(msg)
            logger.log(service_name=SERVICE_NAME, level=0, msg=msg)

        except Exception as e:
            print(e)
            msg = f"Unable to sent Email to : {receiver_email} with subject : {subject}"
            print(msg)
            logger.log(service_name=SERVICE_NAME, level=3, msg=msg)


# sample driver code
if __name__ == "__main__":
    receiver_email = "ias2023.g1@gmail.com"
    subject = "Test"
    body = "Test Body"

    notification = Notification()
    notification.notify(receiver_email, subject, body)
