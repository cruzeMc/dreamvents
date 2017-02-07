from app import mail, Message


def message_sender(message, recipient):
    msg = Message(message,
                  sender="cruze.mcfarlane@gmail.com",
                  recipients=recipient)
    mail.send(msg)
    return True