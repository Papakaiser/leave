
from flask_mail import Mail, Message

mail = None
app = None

def init(app1):
    global mail
    global app
    mail = Mail(app1)
    app = app1



mail_settings = {
    "MAIL_SERVER": 'mail.gjtechghana.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'leaveplanner@gjtechghana.com',
    "MAIL_PASSWORD": 'fridayapril2020'
}

# app.config.update(mail_settings)


def send_mail(mail_addresses, message, subject,copy):
    with app.app_context():
        msg = Message(subject=subject,
                      sender=("Leave Planner","leaveplanner@gjtechghana.com"),

                      # cc = copy,
                      recipients= mail_addresses, # replace with your email for testing
                      body= message )
        if copy:
            msg.cc = copy

        mail.send(msg)


