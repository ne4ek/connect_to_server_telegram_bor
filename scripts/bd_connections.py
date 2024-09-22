from models import *
from aiogram.types.user import User
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import text
init_db()


def regist_tg_user(tg_user: User):
    db = SessionLocal()
    try:
        new_user = Tg_user(
            telegram_id=tg_user.id,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            username=tg_user.username,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"User added with ID: {new_user.id}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()
        return new_user


def add_server_to_db(label, host_name, user_name, password, telegram_user_id):
    db = SessionLocal()
    try:
        tg_user = get_user_from_db(telegram_user_id)
        if tg_user:
            new_host = Host(
                label=label,
                host_name=host_name,
                user_name=user_name,
                password=password,
                user=tg_user,
            )
            db.add(new_host)
            db.commit()
            db.refresh(new_host)
            print(f"Host added with name {host_name}")
        else:
            raise Exception("User is not registed")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


def get_user_from_db(telegram_user_id):
    db = SessionLocal()
    try:
        tg_user = db.query(Tg_user).filter_by(telegram_id=telegram_user_id)

        if not tg_user:
            return False
        return tg_user.first()
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

def get_host_from_db(id: int):
    db = SessionLocal()
    try:
        host = db.query(Host).filter_by(id=id)
        if host:
            return host.first()
        return False
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


def get_all_hosts_for_tg_user(telegram_user_id: int):
    db = SessionLocal()
    try:
        tg_user = tg_user = db.query(Tg_user).options(joinedload(Tg_user.hosts)).filter_by(telegram_id=telegram_user_id)
        if tg_user:
            tg_user = tg_user.first()
            return tg_user.hosts
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


def edit_field_in_host(new_data: str, field: str, host_id: int):
    db = SessionLocal()
    try:
        db.execute(text(f'UPDATE hosts SET {field} = "{new_data}" WHERE id = {host_id};'))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

    
def delete_host_from_db(host_id):
    db = SessionLocal()
    try:
        host = get_host_from_db(int(host_id))
        db.delete(host)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
   