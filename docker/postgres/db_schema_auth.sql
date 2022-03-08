-- Подключение к базе данных
\c users_database;

-- Создание отдельной схемы для пользователей
CREATE SCHEMA IF NOT EXISTS auth_users;

-- Пользователи
CREATE TABLE IF NOT EXISTS auth_users.user
(
    id           uuid PRIMARY KEY,
    email        TEXT NOT NULL,
    password     TEXT NOT NULL,
    full_name    TEXT,
    phone_number TEXT,
    created_at   timestamptz,
    updated_at   timestamptz
);

-- Роли пользователей:
CREATE TABLE IF NOT EXISTS auth_users.roles
(
    id         uuid PRIMARY KEY,
    name       TEXT NOT NULL,
    created_at timestamptz,
    updated_at timestamptz
);

-- Связующая таблица назначенных ролей и их пользователей
CREATE TABLE IF NOT EXISTS auth_users.user_role
(
    id         uuid PRIMARY KEY,
    user_id    uuid REFERENCES auth_users.user (id),
    role_id    uuid REFERENCES auth_users.roles (id),
    updated_at timestamptz,
    created_at timestamptz,
    UNIQUE (user_id, role_id)
);

-- Таблица содержащая историю авторизации
CREATE TABLE IF NOT EXISTS auth_users.auth_history
(
    id         uuid PRIMARY KEY,
    user_id    uuid REFERENCES auth_users.user (id),
    user_agent TEXT NOT NULL,
    created_at timestamptz,
    updated_at timestamptz
);


-- Создание индекса ролей пользователей по столбцам ИД пользователя и ИД роли
CREATE UNIQUE INDEX IF NOT EXISTS user_role ON auth_users.user_role (
                                                                     user_id,
                                                                     role_id
    );
