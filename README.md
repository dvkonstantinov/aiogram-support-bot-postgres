# Aiogram3 Support Bot

Телеграм бот для общения сотрудников поддержки от имени компании с 
пользователями.

## Описание проекта

Идея была заимсвована отсюда: https://habr.com/ru/post/539766/

Пользователи пишут свои вопросы боту компании, бот пересылает эти сообщения 
в чат поддержки, сотрудники поддержки отвечают на эти сообщения через reply.
Основной плюс - анонимизация сотрудников поддержки.

Бот работает в режиме webhook, но может работать и в режиме polling

Для обхода запрета на пересылку сообщения у пользователя, бот копирует 
содержимое и уже затем отправляет его в чат поддержки.

По умолчанию бот отправляет сообщения в один чат поддержки с id, указанным в переменных окружения .env

## Технологический стек
- [Python](https://www.python.org/)
- [Aiogram 3](https://docs.aiogram.dev/en/dev-3.x/)
- [Asyncio](https://docs.python.org/3/library/asyncio.html)
- [Aiohttp](https://github.com/aio-libs/aiohttp)
- [PostgreSQL](https://www.postgresql.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Docker](https://www.docker.com/)
- [Nginx](https://www.nginx.com/)
- [Ubuntu](https://ubuntu.com/)


## Типы контента, которые может пересылать бот
- Текстовые сообщения
- Фотографии
- Группы фотографий (пересылаются по одной)
- Видео
- Аудиозаписи
- Файлы

## Разворачивание образа на личном или vps сервере

### Настройка Nignx

Предполагается, что есть готовый настроенный vps сервер с установленным 
docker, docker-compose и nginx (не контейнерным).

1. Перейти в каталог nginx sites-available
```sh
cd /etc/nginx/sites-available/
```
2. Создать файл с именем вашего домена
```sh
nano domain.example.com
```
3. Внутри написать
```sh
server {
    listen 80;

    server_name domain.example.com;

    location /telegram/ {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:7772;
    }
}
```
server_name - ваш домен с подключенным ssl сертификатом (например, Let's Encrypt)

Вместо /telegram/ можно написать любой путь, на который должны приниматься 
данные. Этот же путь нужно указать в .env файле.
4. Создать ярлык в каталоге sites-enabled
```sh
sudo ln -s /etc/nginx/sites-available/example.com /etc/nginx/sites-enabled/
```
5. Проверить что нет ошибок в конфигурации nginx
```sh
sudo nginx -t
```
6. Перезапустить службу nginx
```sh
sudo systemctl restart nginx
```
7. Установить certbot - ```sudo apt install -y certbot python3-certbot-nginx```
8. Установить https соединение, выпустив ssl сертификат с помощью certbot для вашего домена
```sh
sudo certbot --nginx 
```
9 Добавить автоматическое обновление сертификата ```sudo certbot renew --dry-run ```

Можно на всякий случай еще раз перезапустить nginx

### Запуск бота
1. Создать бота через botfather (см. ниже), добавить бота в группу с сотрудниками поддержки, дать боту права администратора, узнать id группы (см. ниже)
2. Cкопировать этот гит на сервер любым удобным способом
3. Создать .env файл в корне со следующим содержанием:
```sh
TELEGRAM_TOKEN=<телеграм_токен_вашего_бота>
GROUP_ID=<id_группы_или_супергруппы_в_телеграме>
WEBHOOK_DOMAIN=domain.example.com
WEBHOOK_PATH=/telegram/
APP_HOST=0.0.0.0
APP_PORT=7772
DATABASE_URL=postgresql+asyncpg://<postgres_user>:<postgres_password>@<postgres_container_name>:5432/support_bot_db
DB_HOST=<имя_контейнера_с_БД>
DB_PORT=5432
POSTGRES_USER=<postgres_user>
POSTGRES_PASSWORD=<postgres_password>
```
В качестве теста логин пользователя БД, пароль и название БД можно указать postgres. Только для теста, не для продакшена!
4. Запустить сборку docker-образа и его запуск из файла docker-compose.
```sh
sudo docker-compose up -d --build
```
Ключ -d для того чтобы контейнер запустился в фоне.
5. Зайти в контейнер c базой данных, создать базу данных, выдать права на нее пользователю (в данном случае postgres)
```
docker exec -it support-bot-db psql -U postgres
\l #убеждаемся что базы данных нет
create database support_bot_db;
grant all privileges on database support_bot_db to postgres;
\q #выходим из psql
```
6. Применить миграции
```docker exec -it support-bot alembic upgrade head```

### Где что брать
1. WEBHOOK_DOMAIN - домен с подключенным ssl сертификатом

2. WEBHOOK_PATH - URL путь после домена. 

В данном случае WEBHOOK_DOMAIN + WEBHOOK_PATH будет domain.example.com/telegram/

3. Token получаем при создании бота через отца ботов (https://t.me/BotFather)

4. Свой личный id или id группы узнать можно через этого бота. 
   https://t.me/myidbot . Узнать свой id - написать боту в личку, узнать id 
   группы - добавить бота в чат группы (например группы поддержки), затем 
   ввести команду ```/getgroupid``` .

5. APP_HOST - IP на котором будет работать приложение (по умолчанию на хосте 
127.0.0.1, localhost или можно указать 0.0.0.0)

6. APP_PORT - порт, который приложение будет использовать. Порт должен быть 
уникальным и не дублировать порты других приложений, работающих на сервере 
или в Docker.
   

## Запуск в режиме polling (на локальном компьютере)
1. Скопировать гит на локальный компьютер
2. Создать файл .env (см. выше)
3. В файле .env удалить (закомментировать) WEBHOOK_DOMAIN. Прописать свои переменные окружения. Так же прописать переменные окружения в файле docker-compose-postgres-localhost.yaml
4. Установить виртуальное окружение, активировать его, 
   установить зависимости из requirements.txt
```sh
python -m venv venv
pip install -r requirements.txt
```
5. В докере запустить контейнер с базой данных из файла [docker-compose-postgres-localhost.yaml](docker-compose-postgres-localhost.yaml). 
```sh
docker-compose -f docker-compose-postgres-localhost up -d
```
6. Применить миграцию.
```sh
alembic upgrade head
```
7. Если алембик ругается что база данных не существует, создать ее вручную и выйти из psql. Затем попытаться сделать миграцию повторно.
```sh
docker exec -it postgres psql -U postgres
#далее sql
create database support_bot_db;
grant all privileges on database support_bot_db to postgres;
```
5. Запустить main.py ```python main.py```. По умолчанию бот должен подключиться базе данных postgres с именем пользователя postgres и паролем postgres
PS: Для запуска необходим python 3.9 или выше
  
## Команды бота
В **чате поддержки** доступны следующие команды:

```/info``` - Команда вводится через reply на вопрос пользователя и выдает информацию о нем (Имя, 
фамилия, id, никнейм, а также количество сообщений от пользователя и ответов пользователю. Последие 2 - берутся из созданной базы данных.

```/report``` - отчет по количеству клиентов за месяц, сообщений от них и количество ответов администраторов. 

```/report 01.01.2020 15.02.2021``` - отчет за выбранный период. Две любые даты через пробел, по шаблону.

```/ban``` - Команда вводится через reply на вопрос пользователя. Банит пользователя. Сообщения от него будут игнорироваться ботом

```/unban``` - Команда вводится через reply на вопрос пользователя. Разбанивает пользователя.

```/banlist``` - Список забаненных пользователей. Выводит список пользователей в формате id - имя_фамилия

```/registeradmin``` - Регистрирует нового администратора в **чате поддержки**. Также, адинистратор регистриуется автоматически, если ответит на сообщение клиента через reply. Это сделано на случай если забыли зарегистрировать администратора, а он уже отвечает на сообщения.

```/deleteadmin``` - Удаляет права администратора у пользователя в **чате поддержки**. После удаления прав администратора нужно вручную удалить пользователя из группы телеграм.

Если появились вопросы или предложения по улучшению - пишите мне в телеграм, отвечу, обсудим.
## Автор
dvkonstantinov
telegram: https://t.me/Dvkonstantinov

