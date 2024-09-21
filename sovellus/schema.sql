-- Table for users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,                     -- Auto-incrementing user ID
    username VARCHAR(50) UNIQUE NOT NULL,      -- Username for login, must be unique
    password_hash VARCHAR(255) NOT NULL,       -- Hashed password
    role VARCHAR(20) DEFAULT 'user' NOT NULL,  -- Role: 'user' or 'admin', default is 'user'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp for account creation
);

-- Table for discussion areas
CREATE TABLE discussion_areas (
    id SERIAL PRIMARY KEY,                     -- Auto-incrementing discussion area ID
    name VARCHAR(100) NOT NULL,                -- Name of the discussion area
    description TEXT,                          -- Optional description of the discussion area
    is_secret BOOLEAN DEFAULT FALSE NOT NULL,  -- Whether the area is secret, default is false
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp for when the area was created
);

-- Table for threads
CREATE TABLE threads (
    id SERIAL PRIMARY KEY,                     -- Auto-incrementing thread ID
    title VARCHAR(200) NOT NULL,               -- Title of the thread
    user_id INT NOT NULL REFERENCES users(id), -- Foreign key to users table (creator of the thread)
    discussion_area_id INT NOT NULL REFERENCES discussion_areas(id), -- Foreign key to discussion areas table
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp for when the thread was created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- Timestamp for last thread update
);

-- Table for messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,                     -- Auto-incrementing message ID
    thread_id INT NOT NULL REFERENCES threads(id),  -- Foreign key to threads table
    user_id INT NOT NULL REFERENCES users(id),      -- Foreign key to users table (message author)
    content TEXT NOT NULL,                      -- Message content
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp for when the message was created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- Timestamp for last message update
);

-- Table for user permissions in discussion areas
CREATE TABLE user_permissions (
    id SERIAL PRIMARY KEY,                     -- Auto-incrementing permission ID
    user_id INT NOT NULL REFERENCES users(id), -- Foreign key to users table (user with permission)
    discussion_area_id INT NOT NULL REFERENCES discussion_areas(id), -- Foreign key to discussion areas table
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp for when the permission was granted
);