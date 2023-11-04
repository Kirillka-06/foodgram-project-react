# praktikum_new_diplom


# Описание
Сайт для публикации ваших рецептов


# Установка
## Перед началом
- Клонируйте репозиторий на свой компьютер командой в терминале
  `git clone git@github.com:Kirillka-06/foodgram-project-react.git`

## Запуск backend проекта в dev-режиме
- Перейдите в директорию `backend/`
  `cd backend/`
- Создайте и активируйте виртуальное окружение
  `python -m venv venv`
  `source venv/Scripts/activate`
  > для деактивации
  > `deactivate`
- Установите все зависимости
  `pip install -r requirements.txt`
- Создайте `.env` файл по файлу-шаблону `.env.example`
  `nano .env`
- Выполните миграции
  `python mnagage.py migrate`
- Создайте суперюзера django
  `python manage.py createsuperuser`
- Запустите backend сайта на локальном сервере
  `python manage.py runserver`

## Запуск всего проекта в docker-контейнерах
Установите Docker, используя инструкции с официального сайта:
https://www.docker.com/products/docker-desktop/

### Создание Docker-образов
- Замените `username` на ваш логин на DockerHub:
  ```
  cd frontend/
  docker build -t username/kittygram_frontend .
  cd ../backend/
  docker build -t username/kittygram_backend .
  ```
- Загрузите образы на DockerHub:
  ```
  docker push username/foodgraM_frontend
  docker push username/foodgram_backend
  ```
### Запуск Docker-контейнеров
> Если у вас операционная система Linux,
> то перед командами, которые начинаются с docker,
> добавляйте sudo
- Перейдите в директорию `infra/`
  `cd infra/`
- Создайте `.env` файл по файлу-шаблону `.env.example`
  `nano .env`
- Замените названия Docker-образов в файле
  `docker-compose.production.yml` на свои
- Запустите контейнеры командой в терминале
  `docker compose -f docker-compose.production.yml up`
  > Запуск контейнеров в режиме демона
  > `docker compose -f docker-compose.production.yml up -d`
  >
  > Остановка контейнеров
  > `docker compose -f docker-compose.production.yml down`
- Выполните миграции в контейнере backend
  `docker compose -f docker-compose.production.yml exec backend python manage.py migrate`
- Соберите статику в контейнере backend
  `docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic`
- Скопируйте статику в volume static контейнера backend
  `docker compose -f docker-compose.production.yml exec backend cp -r /app/static/. /backend_static/static/`
- Если вы запускаете первый раз, то можете загрузить
  заранее подготовленные ингредиенты в базу данных
  `sudo docker compose -f docker-compose.production.yml exec backend python manage.py loadingredients`
- Создайте суперюзера django
  `sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser`

### Просмотр сайта
- Зайти на главную страницу: http://127.0.0.1:8000/
- Смотреть API проекта: http://127.0.0.1:8000/api/
- Зайти в админ-панель django: http://127.0.0.1:8000/admin/


# Ссылка на сайт
https://foodgram-project.hopto.org/

## Админка django:
- username: kirill
- password: kirkir2006


# Информация об авторе
- Кирилл Кирюшин
- Связь со мной: kiryushin20062006@gmail.com 
