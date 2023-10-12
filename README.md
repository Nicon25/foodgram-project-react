[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646??style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![GitHub](https://img.shields.io/badge/-GitHub-464646??style=flat-square&logo=GitHub)](https://github.com/)
[![docker](https://img.shields.io/badge/-Docker-464646??style=flat-square&logo=docker)](https://www.docker.com/)
[![NGINX](https://img.shields.io/badge/-NGINX-464646??style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![Python](https://img.shields.io/badge/-Python-464646??style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646??style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646??style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)

# Foodgram Project
Foodgram is a website where users can publish recipes, add others' recipes to their favorites, and subscribe to other authors' publications. Site users will also have access to a "Shopping List" feature. It will allow them to create a list of ingredients to buy for preparing selected dishes.

## The current project is available at the following link:
```bash
https://edagram.ddns.net/
```

## Project Launch

### GitHub Setup
- Clone the repository
```bash
git clone git@github.com:Nicon25/foodgram-project-react.git
```
- Navigate to the "Settings" section, then go to "Secrets and Variables" -> "Actions," and add the following Secrets:
```bash
    DOCKER_PASSWORD=<your DockerHub password>
    DOCKER_USERNAME=<your DockerHub username>
    HOST=<IP address of your remote server>
    SSH_KEY=<SSH key of your your remote server>
    SSH_PASSPHRASE=<passphrase of your remote server>
    TELEGRAM_TO=<your Telegram account ID>
    TELEGRAM_TOKEN=<your Telegram bot token>
    USER=<'username for connecting to the remote server'>  
```

### Remote Server Setup
- Create a folder named "foodgram-project-react" on the remote server and navigate to this directory using the following command
```bash
cd foodgram-project-react
```
- Create a .env file using the following command
```bash
sudo nano .env
```
- Populate the file with data as shown below, save (CTRL+O), and close the file (CTRL+X).
```bash
DB_HOST=db
DB_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
SECRET_KEY=<insert a long sequence of characters>
DEBUG=False
ALLOWED_HOST=<insert the server domain/IP>
```
- Install and open the Nginx configuration file
```bash
sudo apt install nginx -y
sudo nano etc/nginx/sites-enabled/default
```
- Fill in Nginx as shown below
```bash
server {
    server_name <insert the server domain/IP>;
    server_tokens off;
    client_max_body_size 20M;

    location / {
        proxy_set_header Host $host;
        proxy_pass http://127.0.0.1:8000;
    }
```
- Install Docker
```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin  
```

### Project startup
- In the Terminal, navigate to the 'foodgram-project-react' project folder and execute the following commands to start the workflow
```bash
  git add .
  git commit -m ''
  git push 
```
- Populate the database with a list of ingredients. On the remote server, enter the following command
```bash
docker-compose -f docker-compose.production.yml exec backend python manage.py load_csv
```

## Available pages
After completing the above actions, the project will be accessible through the following links
- Main page: http://<'your domain'>/
- API: http://<'your domain'>/api/
- Admin: http://<'your domain'>/admin/
