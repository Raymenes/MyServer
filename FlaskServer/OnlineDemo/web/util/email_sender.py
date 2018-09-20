import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, body, to_addr ="ruizeng.usc@gmail.com"):
    server = smtplib.SMTP('smtp.gmail.com', 587)

    # Next, log in to the server
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("jean.jacques.menes@gmail.com", "Z914281r+1s")

    # Send the mail
    from_addr = "jean.jacques.menes@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    body = body
    msg.attach(MIMEText(body, 'plain'))

    server.sendmail(from_addr, to_addr, msg.as_string())

