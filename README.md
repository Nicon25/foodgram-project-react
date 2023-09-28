# Проект Foodgram
Foodgram — это сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Запуск проекта

### Настройка GitHub 
- Клонируйте репозиторий
```bash
git clone git@github.com:Nicon25/foodgram-project-react.git
```
- Перейдите в раздел Settings -> Secrets and Variables -> Actions и добавьте следующие Secrets
```bash
    DOCKER_PASSWORD=<пароль от вашего DockerHub>
    DOCKER_USERNAME=<username вашего DockerHub>
    HOST=<ip вашего удаленного сервера>
    SSH_KEY=<SSH-ключ вашего удаленного сервера>
    SSH_PASSPHRASE=<passphrase вашего удаленного сервера>
    TELEGRAM_TO=<ID вашего Telegram-аккаунта>
    TELEGRAM_TOKEN=<токен вашего Telegram-бота>
    USER=<username для подключения к удаленному серверу>  
```

### Настройка удаленного сервера
- Создайте папку foodgram-project-react на удаленном сервере и перейдите в эту директорию командой
```bash
cd foodgram-project-react
```
- Создайте файл .env командой
```bash
sudo nano .env
```
- Наполните файл данными по примеру ниже, сохраните (CTRL+O) и закройте файл (CTRL+X)
```bash
DB_HOST=db
DB_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
SECRET_KEY=<вписать длинную последовательность символов>
DEBUG=False
ALLOWED_HOST=<вписать домен/IP сервера>
```
- Установите и откройте файл настройки Nginx
```bash
sudo apt install nginx -y
sudo nano etc/nginx/sites-enabled/default
```
- Заполните Nginx по примеру ниже
```bash
server {
    server_name <вписать домен/IP сервера>;
    server_tokens off;
    client_max_body_size 20M;

    location / {
        proxy_set_header Host $host;
        proxy_pass http://127.0.0.1:8000;
    }
```
- Установите Docker
```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin  
```

### Запуск проекта
- В Terminal перейти в папку проект foodgram-project-react и выполнить следудующие команды для запуска workflow
```bash
  git add .
  git commit -m ''
  git push 
```
- Наполните базу данных списком ингредиентов. Для на удаленном сервере введите следующую команду
```bash
docker-compose -f docker-compose.production.yml exec backend python manage.py load_csv
```

## Доступные страницы
После завершения выполнения действий выше проект будет доступен по следующим ссылкам:
- Main page: http://<ваш домен>/
- API: http://<ваш домен>/api/
- Admin: http://<ваш домен>/admin/

## Используемые технологии
- Python
- Django
- PostgreSQL
- Nginx
- Docker
- Github Actions

## Текущий проект доступен по ссылке:
```bash
https://edagram.ddns.net/
```
## Тестовые пользователи
username: nicon (superuser)
email: nic@nic.com
password: parol12345

username: user1
email: user1@gmail.com
password: parol12345

username: user2
email: user2@gmail.com
password: parol12345

## Автор
**[Николай Потапов](https://github.com/Nicon25)**
