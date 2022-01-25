import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# add new email address to the destination emails list
def add_dest_addr(addr):
    with open(r'files/emails.txt', 'r+') as emailFile:
        dest_address = emailFile.readlines()
    addr = addr + '\n'

    if addr in dest_address:
        return -1
    else:
        with open(r'files/emails.txt', 'a') as emailFile:
            emailFile.write(addr)
        return 1

# remove an email address from the destination emails list
def del_dest_addr(addr):
    with open(r'files/emails.txt', 'r+') as emailFile:
        dest_address = emailFile.readlines()
    addr = addr + '\n'

    if addr in dest_address:
        with open(r'files/emails.txt', 'w+') as emailFile:
            dest_address.remove(addr)
            emailFile.writelines(dest_address)
        return 1
    else:
        return -1

def send_email():
    host_email = 'smartcctv.project@gmail.com'
    host_pass = 'SmartCCTVproject'

    # make email
    email_message = MIMEMultipart()
    email_message['From'] = host_email

    # email subject
    email_message['Subject'] = 'Detected Faces From Your Smart CCTV'

    with open('files/detected_names.txt', 'r+') as detectedNamesFile:
        detected = detectedNamesFile.read().splitlines()

    # email body
    timeNow = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    email_message_body = f'<html><head></head><body>'
    email_message_body +=  f'<h2>Smart CCTV</h2>'
    email_message_body += f'<hr>'
    email_message_body += f'<h3>Detected Faces until {timeNow}</h3>'
    email_message_body += f'<ol>'
    for name in detected:
        email_message_body += f'<li>Detected {name}</li>'
    email_message_body += f'</ol>'
    email_message_body += f'</body></html>'

    email_message.attach(MIMEText(email_message_body, 'html'))
    message = email_message.as_string()

    # login to gmail
    smtp_session = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_session.starttls()
    smtp_session.login(host_email, host_pass)

    # get all destination emails
    with open(r'files/emails.txt', 'r+') as emailFile:
        dest_address = emailFile.read().splitlines()

    # send the same email to every destination emails
    for dest in dest_address:
        smtp_session.sendmail(host_email, dest, message)
    
    # stops smtp
    smtp_session.quit()