CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,         -- Username should never be NULL
    password_hash VARCHAR(255) NOT NULL,          -- Password hash should never be NULL
    role VARCHAR(20) NOT NULL DEFAULT 'user',     -- Default role as 'user'
    created_at TIMESTAMP NOT NULL DEFAULT NOW()   -- Automatically set creation date
);

CREATE TABLE discussion_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,                   -- Name is required for a discussion area
    description TEXT,                             -- Description can be NULL
    is_secret BOOLEAN NOT NULL DEFAULT FALSE,     -- Default to not secret
    is_hidden BOOLEAN NOT NULL DEFAULT FALSE,     -- Default to not hidden
    created_at TIMESTAMP NOT NULL DEFAULT NOW()   -- Automatically set creation date
);


CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,                  -- Thread title should never be NULL
    user_id INT REFERENCES users(id) NOT NULL,    -- Every thread must have a creator (user)
    discussion_area_id INT REFERENCES discussion_areas(id) NOT NULL,  -- Must belong to a discussion area
    is_hidden BOOLEAN NOT NULL DEFAULT FALSE,     -- Default to not hidden
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),  -- Automatically set creation date
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()   -- Automatically set update time
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    thread_id INT REFERENCES threads(id) NOT NULL,    -- Every message must belong to a thread
    user_id INT REFERENCES users(id) NOT NULL,        -- Every message must have an author (user)
    is_hidden BOOLEAN NOT NULL DEFAULT FALSE,     -- Default to not hidden
    content TEXT NOT NULL,                            -- Content should never be NULL
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),      -- Automatically set creation date
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()       -- Automatically set update time
);

CREATE TABLE user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) NOT NULL,        -- Permissions must be associated with a user
    discussion_area_id INT REFERENCES discussion_areas(id) NOT NULL, -- And a discussion area
    granted_at TIMESTAMP NOT NULL DEFAULT NOW()       -- Automatically set granted time
);
