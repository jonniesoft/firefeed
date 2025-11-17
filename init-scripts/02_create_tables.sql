-- ============================================================================
-- Создание таблиц для FireFeed
-- ============================================================================

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Таблица кодов верификации
CREATE TABLE IF NOT EXISTS user_verification_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    verification_code VARCHAR(50) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Создание индексов для verification_codes
CREATE INDEX IF NOT EXISTS idx_verification_codes_user_code
    ON user_verification_codes (user_id, verification_code);
CREATE INDEX IF NOT EXISTS idx_verification_codes_expires
    ON user_verification_codes (expires_at);

-- Таблица сброса пароля
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_token
    ON password_reset_tokens (token);

-- Таблица категорий новостей
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Вставка базовых категорий
INSERT INTO categories (id, name) VALUES
    (1, 'World'),
    (2, 'Technology'),
    (3, 'Sports'),
    (4, 'Economics'),
    (5, 'Entertainment'),
    (6, 'Science'),
    (7, 'Health'),
    (8, 'Politics')
ON CONFLICT (id) DO NOTHING;

-- Связь пользователей с категориями
CREATE TABLE IF NOT EXISTS user_categories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, category_id)
);

CREATE INDEX IF NOT EXISTS idx_user_categories_user_id
    ON user_categories (user_id);

-- Источники новостей (RSS ленты)
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(500),
    logo_url VARCHAR(500),
    website_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(name)
);

-- Связь источников с категориями
CREATE TABLE IF NOT EXISTS source_categories (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE(source_id, category_id)
);

-- RSS ленты
CREATE TABLE IF NOT EXISTS rss_feeds (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id) ON DELETE SET NULL,
    url VARCHAR(500) NOT NULL,
    name VARCHAR(255) NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    cooldown_minutes INTEGER DEFAULT 15,
    max_news_per_hour INTEGER DEFAULT 10,
    last_published_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rss_feeds_source
    ON rss_feeds (source_id);
CREATE INDEX IF NOT EXISTS idx_rss_feeds_active
    ON rss_feeds (is_active);

-- Пользовательские RSS ленты
CREATE TABLE IF NOT EXISTS user_rss_feeds (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_rss_feeds_user
    ON user_rss_feeds (user_id);

-- RSS items (новости)
CREATE TABLE IF NOT EXISTS rss_items (
    id VARCHAR(255) PRIMARY KEY,
    feed_id INTEGER NOT NULL REFERENCES rss_feeds(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    summary TEXT,
    url VARCHAR(1000),
    author VARCHAR(255),
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    published BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_rss_items_feed_id
    ON rss_items (feed_id);
CREATE INDEX IF NOT EXISTS idx_rss_items_published_at
    ON rss_items (published_at);
CREATE INDEX IF NOT EXISTS idx_rss_items_processed
    ON rss_items (processed);

-- Переводы новостей
CREATE TABLE IF NOT EXISTS translations (
    id SERIAL PRIMARY KEY,
    news_id VARCHAR(255) NOT NULL REFERENCES rss_items(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMPTZ NULL,
    UNIQUE(news_id, language)
);

CREATE INDEX IF NOT EXISTS idx_translations_news_id
    ON translations (news_id);
CREATE INDEX IF NOT EXISTS idx_translations_language
    ON translations (language);

-- Связь пользователей с Telegram
CREATE TABLE IF NOT EXISTS user_telegram_links (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    telegram_id BIGINT NOT NULL UNIQUE,
    linked_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_telegram_links_user
    ON user_telegram_links (user_id);

-- Триггеры для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Применяем триггеры к нужным таблицам
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sources_updated_at
    BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rss_feeds_updated_at
    BEFORE UPDATE ON rss_feeds
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_rss_feeds_updated_at
    BEFORE UPDATE ON user_rss_feeds
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rss_items_updated_at
    BEFORE UPDATE ON rss_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
