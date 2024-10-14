from db import db
from sqlalchemy.sql import text

def get_areas(user_id,user_role):
    if user_role == "admin":
        sql_query = text("""SELECT 
                    da.id,
                    da.name,
                    da.description,
                    da.is_hidden,
                    COUNT(DISTINCT t.id) AS thread_count,
                    COUNT(m.id) AS message_count,
                    MAX(m.created_at) AS last_message_date
                    FROM
                    discussion_areas da
                    LEFT JOIN threads t ON da.id = t.discussion_area_id
                    LEFT JOIN messages m ON t.id = m.thread_id
                    GROUP BY da.id
                    
                    
                    """)
        result = db.session.execute(sql_query)
        areas = result.fetchall()
        return areas
    else:
        sql_query = text("""
            SELECT 
                da.id,
                da.name,
                da.description,
                da.is_hidden,
                da.is_secret,
                COUNT(DISTINCT t.id) AS thread_count,
                COUNT(m.id) AS message_count,
                MAX(m.created_at) AS last_message_date
            FROM
                discussion_areas da
            LEFT JOIN threads t ON da.id = t.discussion_area_id
            LEFT JOIN messages m ON t.id = m.thread_id
            LEFT JOIN user_permissions up ON da.id = up.discussion_area_id AND up.user_id = :user_id
            WHERE da.is_secret = FALSE OR up.user_id IS NOT NULL
            GROUP BY da.id
        """)
        result = db.session.execute(sql_query,{"user_id":user_id})
        areas = result.fetchall()
        return areas


def create_area(name,description,is_secret,users):
    sql = text("""
    INSERT INTO discussion_areas (name, description, is_secret, created_at)
    VALUES (:name, :description, :is_secret, NOW())
    RETURNING id
    """)
    result = db.session.execute(sql, {"name": name, "description": description, "is_secret": is_secret})
    discussion_area_id = result.fetchone()[0]
    db.session.commit()
    if is_secret:
        print(users)
        for username in users:
            sql_query_user_id = text("SELECT id FROM users WHERE username = :username")
            fetched_user_id = db.session.execute(sql_query_user_id,{"username":username}).fetchone()
            if fetched_user_id:
                sql_permissions = text("""
                INSERT INTO user_permissions (user_id, discussion_area_id, granted_at)
                VALUES (:user_id, :discussion_area_id, NOW())
                """)
                
                db.session.execute(sql_permissions, {"user_id": fetched_user_id[0], "discussion_area_id": discussion_area_id})
                db.session.commit()
    return True


def get_area_by_id(area_id):
    query = text("""
        SELECT id,name FROM discussion_areas WHERE id = :area_id
    """)
    area = db.session.execute(query,{"area_id":area_id}).fetchone()
    if area:
        threads_query = text("""
            SELECT 
                t.id,
                t.title,
                t.created_at,
                u.username AS author,
                COUNT(m.id) AS message_count
                    
            FROM 
                threads t
            JOIN users u ON t.user_id = u.id
            LEFT JOIN messages m ON t.id = m.thread_id
            WHERE t.discussion_area_id = :area_id
            GROUP BY t.id, u.username
            ORDER BY t.created_at DESC
        """)
        threads = db.session.execute(threads_query,{"area_id":area_id}).fetchall()
        return True, area, threads
    else:
        return False,None, None
    
def hide_area(area_id):
    hide_area_query = text("UPDATE discussion_areas SET is_hidden = TRUE WHERE id = :area_id")
    db.session.execute(hide_area_query, {"area_id": area_id})
    db.session.commit()
    return True