from db import db
from sqlalchemy.sql import text
from flask import session

def get_message(message_id):
    query = text("SELECT * FROM messages WHERE id = :message_id")
    message = db.session.execute(query,{"message_id":message_id}).fetchone()

    return message

def edit_message(message_id,content):
    update_query = text("UPDATE messages SET content = :content, updated_at = NOW() WHERE id = :message_id")
    db.session.execute(update_query, {"content": content, "message_id": message_id})
    db.session.commit()

    return True


def delete_message(message_id):
    delete_query = text("UPDATE messages SET is_hidden = True, updated_at = NOW() WHERE id = :message_id")
    db.session.execute(delete_query,{"message_id":message_id})
    db.session.commit()

    return True