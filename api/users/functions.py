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
    user_dict['password'] = hashed_password
    await UsersDAO.create_user(
        data=user_dict,
        session=session,
    )


def create_token(data: dict):
    """
    Генерация токена основываясь на данных пользователя
    """
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, JWT.get("secret"), JWT.get("alg"))
    return encoded_jwt


def update_token(
    user_id: int,
    login: str,
    response: Response,
    is_organizer: bool,
    is_department: bool,
):
    """
    Создание/обновление access и refresh токенов и запихивание их в куки
    """
    token_dict = {
        "sub": user_id,
        "login": login,
        "is_organizer": is_organizer,
        "is_department": is_department,
    }
    token_dict['type'] = "access"
    access_token = create_token(token_dict)
    expire_access = datetime.now(timezone(timedelta(hours=3)).utc) + timedelta(
        minutes=10
    )
    response.set_cookie(
        "access_token",
        access_token,
        expires=expire_access,
        httponly=True,
    )
    token_dict['type'] = "refresh"
    refresh_token = create_token(token_dict)
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
    # берем инфу для создания токена (важно брать именно из UserInfo)
    user_info: UserInfo = await UsersDAOInfo.find_one_or_none(
        session=session,
        filters={'login':user_data.login}
    )
    update_token(
        user_id=str(user_info.id),
        login=user_info.login,
        response=response,
        is_organizer=user_info.is_organizer,
        is_department=user_info.is_department,
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
            user_id=payload.get("sub"),
            login=payload.get("login"),
            response=response,
            is_organizer=payload.get("is_organizer"),
            is_department=payload.get("is_department"),
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
    user = user_model.GetUser(
        id=payload.get("sub"),
        login=payload.get("login"),
        is_organizer=payload.get("is_organizer"),
        is_department=payload.get("is_department"),
    )
    return user


async def create_org(
    session: AsyncSession,
    organaze_model: user_model.OrganizeModel,
    user: UserInfo
):
    if not user.is_department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access denied",
        )
    org_check = await OrganizeInfoDAO.find_one_or_none(
        session=session,
        filters={"user_id": organaze_model.user_id}
    )
    if org_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="this user already organizer"
        )
    await OrganizeInfoDAO.insert_data(
        session,
        organaze_model.model_dump()     
    )
    await UsersDAOInfo.update_data(
        session=session,
        values={"is_organizer": True},
        filters={"id": organaze_model.user_id}
    )