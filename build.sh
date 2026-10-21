#!/usr/bin/env bash
set -e

echo "==> Установка зависимостей..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "==> Сборка статических файлов..."
python manage.py collectstatic --noinput

echo "==> Выполнение миграций..."
python manage.py migrate --noinput

echo "==> Наполнение базы данных кафедры 317..."
python manage.py seed_mai_data

echo "==> Сборка успешно завершена!"