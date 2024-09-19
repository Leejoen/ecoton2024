import users.model as user_model
from users.dao import UsersDAO, UsersDAOInfo, OrganizeInfoDAO
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from database.config import JWT
from datetime import datetime, timedelta, timezone
from fastapi import Request, Response, status, HTTPException, Depends
from database.schemas import UserInfo
import hashlib
import uuid
import base64
from send_mail import get_mail_template, send_email


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(incoming_password, db_password) -> bool:
    """
    Проверка валидности пароля
    """
    return pwd_context.verify(incoming_password, db_password)


def get_password_hash(password):
    """
    Хеширование пароля пользователя
    """
    return pwd_context.hash(password)


async def register_user(user_data: user_model.UserResgisetr, session: AsyncSession):
    """
    Создание пользователя в БД
    """
    # проверяем его наличие
    existing_user = await UsersDAO.find_one_or_none(
        session=session,
        filters={"login": user_data.login},
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="такой пользователь уже существует",
        )
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.model_dump()
    # Генерируем уникальный UUID
    unique_id = uuid.uuid4() 
    # Преобразуем UUID в строку и кодируем ее с помощью base64
    uidb64 = base64.urlsafe_b64encode(unique_id.bytes).rstrip(b'=').decode('utf-8')
    combined_data = f"{user_data.login}-{uidb64}"
    verify_token = hashlib.sha256(combined_data.encode()).hexdigest()
    user_dict['verify_token'] = verify_token
    user_dict['password'] = hashed_password
    # создаем юзера
    await UsersDAO.create_user(
        data=user_dict,
        session=session,
    )
    # отправляем ему письмо с уникальной ссылкой
    active_url = f'https://postum.su/email_activate/{verify_token}'
    mail_template = get_mail_template(active_url)
    send_email(
        to_email=user_data.login,
        subject="Подтверждение Email",
        message_body=mail_template
    )


def create_token(data: dict):
    """
    Генерация токена основываясь на данных пользователя
    """
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, JWT.get("secret"), JWT.get("alg"))
    return encoded_jwt


def update_token(
    user_dict: dict,
    response: Response,
):
    """
    Создание/обновление access и refresh токенов и запихивание их в куки
    """
    user_dict['type'] = "access"
    access_token = create_token(user_dict)
    expire_access = datetime.now(timezone(timedelta(hours=3)).utc) + timedelta(
        minutes=10
    )
    response.set_cookie(
        "access_token",
        access_token,
        expires=expire_access,
        httponly=True,
    )
    user_dict['type'] = "refresh"
    refresh_token = create_token(user_dict)
    expire_refresh = datetime.now(timezone(timedelta(hours=3)).utc) + timedelta(days=30)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        expires=expire_refresh,
        httponly=True,
    )

    return access_token


async def login_user(
    response: Response,
    user_data: user_model.UserLogin,
    session: AsyncSession,
) -> user_model.UserInfo:
    """
    Аутентификация пользователя в системе
    """    
    # проверяем его наличие в системе
    user = await UsersDAO.find_one_or_none(
        session=session,
        filters={'login':user_data.login},
    )
    # проверяем валидность введенных данных
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="введены неверные данные",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Подтвердите почту!"
        )
    # берем инфу для создания токена (важно брать именно из UserInfo)
    user_info: UserInfo = await UsersDAOInfo.find_one_or_none(
        session=session,
        filters={'login':user_data.login}
    )
    user_dict = {
        "id": str(user_info.id),
        "login": user_info.login,
        "is_organizer": user_info.is_organizer,
        "is_department": user_info.is_department,
    }
    update_token(
        user_dict=user_dict,
        response=response,
    )
    return user_model.UserInfo.model_validate(user_info)


def get_token(request: Request, response: Response):
    """
    Проверка наличия токенов и обновление access токена при наличии refresh
    """
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not access_token and refresh_token:
        try:
            payload = jwt.decode(refresh_token, JWT.get("secret"), JWT.get("algoritm"))
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{e}",
            )
        access_token = update_token(
            user_dict=payload,
            response=response,
        )

    return access_token


async def get_current_user(
    token: str = Depends(get_token)
) -> user_model.GetUser:
    """
    Проверка пользователя (залогинен или нет)
    """
    try:
        payload = jwt.decode(token, JWT.get("secret"), JWT.get("algoritm"))
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{e}",
        )
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="не тот токен",
        )
    user = user_model.GetUser(**payload)
    return user


async def create_org(
    session: AsyncSession,
    organaze_model: user_model.OrganizeModel,
    user: UserInfo
):
    """
    Создать организатора
    Доступно для сотрудников департамента (модеров)

    """
    if not user.is_department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )
    org_check = await OrganizeInfoDAO.find_one_or_none(
        session=session,
        filters={"user_id": organaze_model.user_id}
    )
    # проверим, не является ли юзер уже организатором
    # у нас пока один пользователь - может быть одной организацией 
    if org_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="this user already organizer"
        )
    # если все ок, то создаем организацию
    # и даем права орга юзеру 
    await OrganizeInfoDAO.insert_data(
        session,
        organaze_model.model_dump()     
    )
    await UsersDAOInfo.update_data(
        session=session,
        values={"is_organizer": True},
        filters={"id": organaze_model.user_id}
    )


async def email_activate(
    session: AsyncSession,
    verify_token: str,
):
    """
    Подтверждение пользователем почты
    """
    # проверяем тот ли пользователь подверждает почту
    check_user_login = await UsersDAO.check_user(
        session=session,
        filters={"verify_token":verify_token}
    )
    if not check_user_login:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="this is not your mail!"
        )
    # активируем нашего юзера
    await UsersDAO.update_data(
        session=session,
        values={"is_active": True},
        filters={'login': check_user_login}
    )
