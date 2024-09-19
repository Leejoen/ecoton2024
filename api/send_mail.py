import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database.config import MAIL


# Шаблон письма
def get_mail_template(url):
    template = f'<h1 style="text-align: center; font-size: 32px; display: flex;">' \
               f' <span style="color: #21628c;">Экотон</span>' \
               f'<span style="color: #ccc;">Собрания</span></h1>' \
               f'<p>Перейдите по <a href="{url}" style="color: #21628c; font-size: 18px;">' \
               f'ссылке</a> для подтверждения эл. почты</p><p>Если вы не вводили свою почту на сайте postum.su,' \
               f' ни в коем случае не переходите по ссылке</p>'
    return template


# Отправка почты
def send_email(to_email, subject, message_body):
    # Настройки SMTP-сервера
    smtp_server = MAIL.get("smtp_server")
    smtp_port = MAIL.get("smtp_port")
    login = MAIL.get("login")
    password = MAIL.get("password")

    # Создаем объект MIME
    msg = MIMEMultipart()
    msg['From'] = login
    msg['To'] = to_email
    msg['Subject'] = subject

    # Добавляем тело письма
    msg.attach(MIMEText(message_body, 'html'))  # Можно также использовать 'html' для HTML-сообщений

    try:
        # Устанавливаем соединение с SMTP-сервером
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Обязательно для TLS
        server.login(login, password)

        # Отправляем письмо
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        print(f"Письмо отправлено на {to_email}")

    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")

    finally:
        server.quit()