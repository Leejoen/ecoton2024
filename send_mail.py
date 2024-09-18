import datetime
import hashlib
import uuid
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Шаблон письма
def get_mail_template(url):
    template = f'<h1 style="text-align: center; font-size: 32px; display: flex;">' \
               f' <span style="color: #21628c;">Экотон</span>' \
               f'<span style="color: #ccc;">Собрания</span></h1>' \
               f'<p>Перейдите по <a href="{url}" style="color: #21628c; font-size: 18px;">' \
               f'ссылке</a> для подтверждения эл. почты</p><p>Если вы не вводили свою почту на сайте postum.su,' \
               f' ни в коем случае не переходите по ссылке</p>'
    return template


# Генерируем уникальную ссылку для активации почты
def generate_email_activate_link(mail):

    unique_id = uuid.uuid4()  # Генерируем уникальный UUID

    # Преобразуем UUID в строку и кодируем ее с помощью base64
    uidb64 = base64.urlsafe_b64encode(unique_id.bytes).rstrip(b'=').decode('utf-8')

    combined_data = f"{mail}-{uuid.uuid4()}"

    token = hashlib.sha256(combined_data.encode()).hexdigest()  # Уникальный набор цифр

    active_url = f'https://postum.su/email_activate/{uidb64}/{token}/{mail}'

    # Добавляем 50 минут к текущему времени
    expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=50)

    return {'url': active_url, 'mail': mail, 'expiration_time': str(expiration_time)}


# Отправка почты
def send_email(to_email, subject, message_body):
    # Настройки SMTP-сервера
    smtp_server = "smtp.mail.ru"
    smtp_port = 2525  # Порт для TLS
    login = "mafilms@mail.ru"  # email, с которого отправляется
    password = "6DdMPihH2T3rbaJkzWbp"  # Пароль для работы с почтой

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


# Этот код нужно при отправке формы выполнять

TO_EMAIL = "magomedabdulaev915@mail.ru"  # Здесь ставить почту которую указал пользователь при регистрации
send_email(
    TO_EMAIL,
    "Подтверждение Email",
    get_mail_template(generate_email_activate_link(TO_EMAIL)['url'])
)


