import smtplib
import ssl
from email.message import EmailMessage
from decouple import config

SENDER_EMAIL = "ias2023.g1@gmail.com"
SENDER_PASSWORD = "lhjzqidvggrpmnkq"


def sendEmail(receiver_email, subject, body):
    em = EmailMessage()
    em["From"] = SENDER_EMAIL
    em["To"] = receiver_email
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            x = smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            r = smtp.sendmail(SENDER_EMAIL, receiver_email, em.as_string())
        print("Email Sent Successfully.")

    except Exception as e:
        print(e)
        print("Unable to send Email.")


# sample driver code
if __name__ == "__main__":
    while True:
        receiver_email = input("Enter Email : ")
        subject = input("Enter Subject : ")
        body = input("Enter Body : ")

        sendEmail(receiver_email, subject, body)
