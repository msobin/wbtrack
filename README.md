### WBTrack

## Описание
Telegram-бот для отслеживания цен на товары в интернет-магазине wildberries 

## Требования

* [docker](https://www.docker.com/) 
* [docker-compose](https://docs.docker.com/compose/install/) 

## Установка

* склонируйте проект
* зарегистрируйте новго бота следуя [инструкциям](https://tlgrm.ru/docs/bots#kak-sozdat-bota)
* переименуйте файлы: .env_example в .env, docker-compose.example.yml в docker-compose.yml 
* пропишите токен зарегистрированного бота в файле .env (параметр: BOT_TOKEN)
* соберите контейнер командой `docker-compose build && docker-compose run app python app/init_db.py`  

## Использование

* запустите контейнер командой `docker-compose up -d`
