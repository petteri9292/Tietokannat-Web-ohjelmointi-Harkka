CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(20),
    created_at TIMESTAMP
);

CREATE TABLE discussion_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    is_secret BOOLEAN,
    created_at TIMESTAMP
);

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    user_id INT REFERENCES users,
    discussion_area_id INT REFERENCES discussion_areas,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    thread_id INT REFERENCES threads,
    user_id INT REFERENCES users,
    content TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    discussion_area_id INT REFERENCES discussion_areas,
    granted_at TIMESTAMP
);
