from database.my_engine import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.schemas import UserInfo
import users.model as user_model
import users.functions as auth_func
from users.functions import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Auth & Users"]
)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: user_model.UserResgisetr,
    session: AsyncSession = Depends(get_db)
):
    await auth_func.register_user(user_data, session)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=user_model.UserInfo
)
async def login_user(
    response: Response,
    user_data: user_model.UserLogin,
    session: AsyncSession = Depends(get_db)
):
    return await auth_func.login_user(response, user_data, session)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK
)
async def logout_user(
    response: Response
):
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')


@router.post(
    '/create_org',
    status_code=status.HTTP_201_CREATED,
    summary="Создание организатора"
)
async def create_org(
    user_model: user_model.OrganizeModel,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await auth_func.create_org(session, user_model, user)


@router.get(
    '/email_activate/{verify_token}',
    status_code=status.HTTP_200_OK,
    summary="Подтверждение почты пользователя"
)
async def email_activate(
    verify_token,
    session: AsyncSession = Depends(get_db),
):
    return await auth_func.email_activate(session, verify_token)