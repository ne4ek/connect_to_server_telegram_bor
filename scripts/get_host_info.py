from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from main import router
from scripts.server_connection import *


class HostInfo(StatesGroup):
    waiting_for_host_name = State()
    waiting_for_user_name = State()
    waiting_for_password = State()


@router.message(HostInfo.waiting_for_host_name)
async def process_host_name(message: Message, state: FSMContext):

    host_name = message.text
    # print(message.from_user)
    await state.update_data(host_name=host_name)
    await message.answer("Enter the1 user name")
    await state.set_state(HostInfo.waiting_for_user_name)


@router.message(HostInfo.waiting_for_user_name)
async def process_user_name(message: Message, state: FSMContext):
    user_name = message.text
    await state.update_data(user_name=user_name)
    await message.answer("Enter the password")
    await state.set_state(HostInfo.waiting_for_password)


@router.message(HostInfo.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text
    await state.update_data(password=password)


