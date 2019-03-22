from threading import Thread

from flask_mail import Message

from app import app, mail


def send_async_email(msg):
    with app.app_context():
        mail.send(msg)


def send_text(email, title, content):
    msg = Message(title, recipients=[email], charset='utf-8')
    msg.body = content
    thr = Thread(target=send_async_email, args=[msg])
    thr.start()


def send_html(email, title, content):
    msg = Message(title, recipients=[email], charset='utf-8')
    msg.html = content
    thr = Thread(target=send_async_email, args=[msg])
    thr.start()
