from common.models import User, UserProduct


class UserService:
    def __init__(self, db):
        self.session = db.get_session()

    def get_user(self, telegram_id):
        user = self.session.query(User).filter_by(telegram_id=telegram_id).first()

        if not user:
            self.create_user(telegram_id)
            user = self.session.query(User).filter_by(telegram_id=telegram_id).first()

        return user

    def create_user(self, telegram_id):
        self.session.add(User(telegram_id=telegram_id))
        self.session.commit()

    def logout(self, telegram_id):
        user = self.get_user(telegram_id)

        self.session.query(UserProduct).filter_by(user_id=user.id).delete()
        self.session.delete(user)
        self.session.commit()
