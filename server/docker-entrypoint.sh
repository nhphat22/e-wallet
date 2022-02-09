#!/bin/sh

set -e

# flask db upgrade

# export FLASK_APP=main 
# export FLASK_DEBUG=1 
# export FLASK_ENV=development

# gunicorn -c gunicorn.config.py server:app
python3 main.py create_db
python3 main.py db init
python3 main.py db migrate
python3 main.py runserver