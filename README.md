# Docker Lab — Task Manager

Веб-приложение для управления задачами (to-do list), контейнеризированное с помощью Docker Compose.
Стек: **Nginx** (фронтенд), **Flask** (бэкенд API), **PostgreSQL** (база данных).

## Быстрый старт

```bash
cp .env.example .env
docker compose up -d --build
```

Откройте http://localhost в браузере.

## Переменные окружения

Файл `.env` (не попадает в Git, создаётся из `.env.example`):

| Переменная          | Описание                | Пример     |
|---------------------|-------------------------|------------|
| `POSTGRES_DB`       | Имя базы данных         | `taskdb`   |
| `POSTGRES_USER`     | Пользователь PostgreSQL | `appuser`  |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL       | `changeme` |
