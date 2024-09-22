from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from scripts.bd_connections import get_all_hosts_for_tg_user, get_host_from_db, edit_field_in_host, delete_host_from_db
from scripts.server_connection import connect_to_server, exit_from_server
from main import router
import paramiko
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import time

class WaitingForCommands(StatesGroup):
    waiting_for_commands = State()

class WaitingForNewNameForField(StatesGroup):
    waiting_for_new_name_for_field = State()
    
class WaitingForConfirmDeleting(StatesGroup):
    waiting_for_confirm_deleting = State()

edits = {"label":"Edit label", "host_name":"Edit address", "user_name":"Edit user", "password":"Edit password"}

@router.message(Command("myHosts"))
async def my_hosts(message: Message):
    hosts = get_all_hosts_for_tg_user(message.from_user.id)
    buttons = [[InlineKeyboardButton(text=str(host.label), callback_data=f"server_{host.id}")] for host in hosts]
    if buttons:
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    if hosts:
        await message.answer("Your servers:", reply_markup=keyboard)
    else:
        await message.answer("You don't have any servers registered.")


@router.callback_query(lambda c: c.data.startswith("server_"))
async def handle_server_selection(callback_query: CallbackQuery):
    server_number = callback_query.data.split("server_")[1]
    server = get_host_from_db(server_number)
    response_text = f"Server information\nLabel: {server.label}\nAddress: {server.host_name}\nUser: {server.user_name}\nPassword: {server.password}"
    edit_buttons = [[InlineKeyboardButton(text=f"{val}", callback_data=f"edit-server-{key}-{server_number}")] for key, val in edits.items()]
    edit_buttons.insert(0, [InlineKeyboardButton(text="Connect", callback_data=f"connect_to_server_{server_number}")])
    edit_buttons.append([InlineKeyboardButton(text="Delete", callback_data=f"delete_host_{server_number}")])
    edit_buttons.append([InlineKeyboardButton(text="Back", callback_data="go_to_back_my_hosts")])
    response_buttons = InlineKeyboardMarkup(inline_keyboard=edit_buttons)
    await callback_query.message.edit_text(response_text, reply_markup=response_buttons)
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith("edit-server-"))
async def edit_server(callback_query: CallbackQuery, state: FSMContext):
    field, server_number = (callback_query.data.split("server-")[1]).split('-')
    await callback_query.answer()
    await state.update_data(field=field)
    await state.update_data(server_number=server_number)
    await callback_query.message.answer(f"Enter the new name for {edits[field].split(' ')[1]}")
    await state.set_state(WaitingForNewNameForField.waiting_for_new_name_for_field)


@router.message(WaitingForNewNameForField.waiting_for_new_name_for_field)
async def process_waiting_for_new_name_for_field(message: Message, state: FSMContext): 
    state_data = await state.get_data()
    new_data = message.text
    field = state_data["field"]
    server_number = state_data["server_number"]
    try:
        edit_field_in_host(new_data, field, server_number)
    except Exception as e:
        await message.answer("Something went wrong")
        raise e
    else:
        await message.answer("Changed")   


@router.callback_query(lambda c: c.data == "go_to_back_my_hosts")
async def go_back(callback_query: CallbackQuery):
    hosts = get_all_hosts_for_tg_user(callback_query.from_user.id)
    buttons = [[InlineKeyboardButton(text=str(host.label), callback_data=f"server_{host.id}")] for host in hosts]
    if buttons:
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    if hosts:
        await callback_query.message.edit_text("Your servers:", reply_markup=keyboard)
    else:
        await callback_query.message.edit_text("You don't have any servers registered.")


@router.callback_query(lambda c: c.data.startswith("connect_to_server"))
async def handle_connect_to_server(callback_query: CallbackQuery, state: FSMContext):
    server_number = callback_query.data.split("connect_to_server_")[1]
    server = get_host_from_db(server_number)
    try:
        ssh = connect_to_server(server.host_name, server.user_name, server.password)
    except Exception as e:
        await callback_query.answer()
        await callback_query.message.answer("Something went wrong")
        raise e
    await callback_query.message.answer("You was connected. Type 'exit from server' of 'efs1' for disconnect.")
    channel: paramiko.Channel = ssh.invoke_shell()
    time.sleep(1)
    output = channel.recv(1024).decode()
    await callback_query.message.answer(output)
    await state.update_data(ssh=ssh)
    await state.update_data(channel=channel)
    await state.set_state(WaitingForCommands.waiting_for_commands)
    


@router.message(WaitingForCommands.waiting_for_commands)
async def process_waiting_for_commands(message: Message, state: FSMContext):
    command = message.text
    data = await state.get_data()
    channel = data["channel"]
    ssh = data["ssh"]
    print(command)
    if command == "exit from server" or command == "efs1":
        exit_from_server(ssh, channel)
        await message.answer("You was disconnected")
        await state.clear()
    else:
        channel.send(command + '\n')
        time.sleep(2)
        output = channel.recv(1024).decode('utf-8')
        await message.answer(output)
        
        
        
@router.callback_query(lambda c: c.data.startswith("delete_host_"))
async def handle_delete_host(callback_query: CallbackQuery, state: FSMContext):
    server_number = callback_query.data.split("delete_host_")[1]
    await state.update_data(server_number=server_number)
    await callback_query.answer()
    await callback_query.message.answer("Confirm the deleting, type 'yes' or 'y'")
    await state.set_state(WaitingForConfirmDeleting.waiting_for_confirm_deleting)
    
    
@router.message(WaitingForConfirmDeleting.waiting_for_confirm_deleting)
async def process_waiting_for_confirm_deleting(message: Message, state: FSMContext):
    message_text = message.text
    data = await state.get_data()
    server_number = data["server_number"]
    if message_text in "yes":
        try:
            delete_host_from_db(server_number)
        except Exception as e:
            await message.answer("Something went wrong")
            raise e
        else:
            await message.answer("Deleted")
        await state.clear()
    else:
        await message.answer("Unconfirmed")
        await state.clear()