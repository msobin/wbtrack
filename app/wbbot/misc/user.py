from common.models import User


def get_user(telegram_id, session):
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if not user:
        create_user(telegram_id, session)
        user = session.query(User).filter_by(telegram_id=telegram_id).first()

    return user


def create_user(telegram_id, session):
    session.add(User(telegram_id=telegram_id))
    session.commit()
