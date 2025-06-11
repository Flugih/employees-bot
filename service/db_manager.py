from sqlalchemy.exc import SQLAlchemyError
from domain import Chat, Database


class DBManager:
    def __init__(self):
        self.database = Database()
        self.session = self.database.get_session()

    async def create_table(self):
        try:
            Chat.__table__.create(bind=self.session.bind, checkfirst=True)
        except SQLAlchemyError:
            self.session.rollback()

    async def add_record(self, chat_id, status: bool):
        try:
            chat = self.session.query(Chat).filter_by(chat_id=chat_id).first()

            if chat:
                chat.status = status
            else:
                new_chat = Chat(chat_id=chat_id, status=status)
                self.session.add(new_chat)

            self.session.commit()

        except SQLAlchemyError:
            self.session.rollback()

    async def read_records(self):
        try:
            return [(chat.chat_id, chat.status) for chat in self.session.query(Chat).all()]
        except SQLAlchemyError:
            return []

    async def update_status(self, chat_id, new_status: bool):
        try:
            chat = self.session.query(Chat).filter_by(chat_id=chat_id).first()

            if chat:
                chat.status = new_status
            else:
                await self.add_record(chat_id, new_status)

            self.session.commit()

        except SQLAlchemyError:
            self.session.rollback()

    async def get_status(self, chat_id) -> bool | None:
        try:
            chat = self.session.query(Chat).filter_by(chat_id=chat_id).first()

            if chat:
                return chat.status

            return None

        except SQLAlchemyError:
            return None

    async def delete_chat(self, chat_id):
        try:
            chat = self.session.query(Chat).filter_by(chat_id=chat_id).first()

            if chat:
                self.session.delete(chat)
                self.session.commit()

        except SQLAlchemyError:
            self.session.rollback()

    async def get_all_chat_ids(self):
        try:
            return [chat.chat_id for chat in self.session.query(Chat).all()]
        except SQLAlchemyError:
            return []

    async def ensure_chat_exists(self, chat_id, status: bool):
        try:
            if not self.session.query(Chat).filter_by(chat_id=chat_id).first():
                await self.add_record(chat_id, status)
        except SQLAlchemyError:
            return None

    async def get_whitelist(self, chat_id):
        chat = self.session.query(Chat).filter_by(chat_id=chat_id).first()

        if chat and chat.whitelist:
            return chat.whitelist.split(",")

        return []

    async def add_to_whitelist(self, chat_id, user_id):
        try:
            chat = self.session.query(Chat).filter_by(chat_id=chat_id).first()
            if not chat:
                return

            whitelist = chat.whitelist.split(",") if chat.whitelist else []
            if str(user_id) in whitelist:
                return

            whitelist.append(str(user_id))
            chat.whitelist = ",".join(whitelist)
            self.session.commit()

        except SQLAlchemyError:
            self.session.rollback()

    async def remove_from_whitelist(self, chat_id, user_id):
        try:
            chat = self.session.query(Chat).filter_by(chat_id=chat_id).first()
            if not chat:
                return

            if not chat.whitelist:
                return

            whitelist = chat.whitelist.split(",")

            if str(user_id) not in whitelist:
                return

            whitelist.remove(str(user_id))
            chat.whitelist = ",".join(whitelist) if whitelist else None
            self.session.commit()

        except SQLAlchemyError:
            self.session.rollback()
