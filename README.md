python -m venv venv

venv\Scripts\activate   

pip install django channels channels-redis daphne

docker run -d -p 6379:6379 redis 

daphne card_game_backend.asgi:application
