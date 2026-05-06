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

## Полезные команды

```bash
docker compose up -d --build   # запустить
docker compose down            # остановить (данные сохраняются)
docker compose down -v         # остановить + удалить тома (данные удаляются!)
docker compose ps              # статус сервисов
docker compose logs -f backend # логи бэкенда
docker compose exec backend sh # войти в контейнер
docker compose exec postgres psql -U appuser -d taskdb
docker network ls
docker volume ls
```

## Персистентность данных и `docker compose down -v`

- **`docker compose down`** — тома сохраняются, данные на месте после перезапуска.
- **`docker compose down -v`** — удаляет именованный том `pgdata`, все данные PostgreSQL **безвозвратно удаляются**.

### Результаты теста

1. Запущен стек, добавлены задачи через UI и curl
2. `docker compose down` → `docker compose up -d` — задачи сохранились ✅
3. `docker compose down -v` → `docker compose up -d` — БД пустая ✅
