### WBTrack

## Description
Telegram Bot to track product prices at wildberries online store 

## Requirements

* [docker](https://www.docker.com/) 
* [docker-compose](https://docs.docker.com/compose/install/) 

## Installation

* clone the project
* register a new bot by following [instructions](https://tlgrm.ru/docs/bots#kak-sozdat-bota)
* rename the files: .env_example to .env, docker-compose.example.yml to docker-compose.yml 
* write the token of the registered bot in the .env file (parameter: BOT_TOKEN).
* assemble the container by command `docker-compose build && docker-compose run app python init_db.py && docker-compose run app python wbscrapy/proxies.py `  

## Usage

* run the container with the command `docker-compose up -d`
