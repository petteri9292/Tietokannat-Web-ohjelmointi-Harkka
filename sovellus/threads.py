from db import db
from sqlalchemy.sql import text
from flask import session


def create_thread(title,user_id,area_id,first_message):
    insert_thread_query = text("""
        INSERT INTO threads (title, user_id, discussion_area_id, created_at, updated_at)
        VALUES (:title, :user_id, :discussion_area_id, NOW(), NOW())
        RETURNING id
    """)
    user_id = session.get("user_id")
    result = db.session.execute(insert_thread_query, {
        "title": title,
        "user_id": user_id,
        "discussion_area_id": area_id

    })
    thread_id = result.fetchone()[0]
    db.session.commit()

    insert_message_query = text("""
        INSERT INTO messages (content, thread_id, user_id, created_at, updated_at)
        VALUES (:content, :thread_id, :user_id, NOW(), NOW())
    """)
    
    db.session.execute(insert_message_query, {
        "content": first_message,
        "thread_id": thread_id,
        "user_id": user_id
    })
    db.session.commit()

    return thread_id


def get_thread(thread_id):
    query = text("""
        SELECT id,title,user_id FROM threads WHERE id = :thread_id ORDER BY id DESC
    """)
    thread = db.session.execute(query,{"thread_id":thread_id}).fetchone()
    if thread:
        messages_query = text("""
            SELECT 
                m.content, 
                m.created_at, 
                u.username,
                m.id,
                m.updated_at,
                m.is_hidden
            FROM messages m
            LEFT JOIN users u ON m.user_id = u.id
            WHERE m.thread_id = :thread_id
            ORDER BY m.created_at ASC
        """)
        messages = db.session.execute(messages_query,{"thread_id":thread_id}).fetchall()

        area_query = text("""
            SELECT
                da.id,da.is_secret
            FROM
                discussion_areas da
            JOIN
                threads t
            ON 
                da.id = t.discussion_area_id
            WHERE
                t.id = :thread_id
        """)
        area = db.session.execute(area_query,{"thread_id":thread_id}).fetchone()
        if area[1]:
            if not area[0] in session["permissions"] and session["role"] != "admin":
                return False, False, False
            else:
                return area, thread,messages
        else:
            return area, thread,messages
    else:
        return False, False, False
    

def add_message(reply_content,thread_id,user_id):
    insert_message_query = text("""
        INSERT INTO messages (content, thread_id, user_id, created_at, updated_at)
        VALUES (:content, :thread_id, :user_id, NOW(), NOW())
    """)
    
    db.session.execute(insert_message_query, {
        "content": reply_content,
        "thread_id": thread_id,
        "user_id": user_id
    })
    db.session.commit()


def edit_thread(thread_id, title):
    update_query = text("UPDATE threads SET title = :title, updated_at = NOW() WHERE id = :thread_id")
    db.session.execute(update_query, {"title": title, "thread_id": thread_id})
    db.session.commit()
    return True


def delete_thread(thread_id):
    delete_query = text("UPDATE threads SET is_hidden = True, updated_at = NOW() WHERE id = :thread_id")
    db.session.execute(delete_query, {"thread_id": thread_id})
    db.session.commit()
    return True
