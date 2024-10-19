from db import db
from sqlalchemy.sql import text

def search(query):
    sql_query = text("""
        SELECT m.content AS content, 
            m.updated_at AS updated_at,
            u.username AS username,
            da.name AS area,
            t.title AS thread,
            da.id AS area_id,
            t.id AS thread_id
        FROM messages m
        JOIN threads t ON m.thread_id = t.id
        JOIN discussion_areas da ON t.discussion_area_id = da.id 
        JOIN users u ON m.user_id = u.id
        WHERE m.content LIKE :query
        AND da.is_secret = FALSE
        AND da.is_hidden = FALSE
    """)
    result = db.session.execute(sql_query,{"query":"%"+query+"%"}) 
    messages = result.fetchall()

    return messages