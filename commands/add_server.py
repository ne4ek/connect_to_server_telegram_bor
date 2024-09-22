from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from main import router
from scripts.bd_connections import add_server_to_db



class HostInfo(StatesGroup):
    waiting_for_host_label = State()
    waiting_for_host_name = State()
    waiting_for_user_name = State()
    waiting_for_password = State()


@router.message(Command("addServer"))
async def add_server(message: Message, state: FSMContext):
    await message.answer("Enter the label")
    await state.set_state(HostInfo.waiting_for_host_label)


@router.message(HostInfo.waiting_for_host_label)
async def process_label(message: Message, state: FSMContext):
    label = message.text
    await state.update_data(label=label)
    await message.answer("Enter the host name")
    await state.set_state(HostInfo.waiting_for_host_name)


@router.message(HostInfo.waiting_for_host_name)
async def process_host_name(message: Message, state: FSMContext):
    host_name = message.text
    await state.update_data(host_name=host_name)
    await message.answer("Enter the user name")
    await state.set_state(HostInfo.waiting_for_user_name)


@router.message(HostInfo.waiting_for_user_name)
async def process_user_name(message: Message, state: FSMContext):
    user_name = message.text
    await state.update_data(user_name=user_name)
    await message.answer("Enter the password")
    await state.set_state(HostInfo.waiting_for_password)


@router.message(HostInfo.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    data = await state.get_data()
    password = message.text
    await state.update_data(password=password)
    try:
        add_server_to_db(
            label=data["label"],
            host_name=data["host_name"],
            user_name=data["user_name"],
            password=password,
            telegram_user_id=message.from_user.id,
        )
    except Exception as e:
        await message.answer("Something went wrong")
        raise e
    else:
        await message.answer("Serer was added")
        await state.clear()
