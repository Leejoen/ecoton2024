from database.my_engine import get_db
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
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


@router.get(
    "/check_user",
    status_code=status.HTTP_200_OK
)
async def check_user(
    user: user_model.UserInfo = Depends(get_current_user)
):
    return await auth_func.check_user()