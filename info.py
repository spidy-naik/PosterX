import re
import os
from os import environ, getenv

id_pattern = re.compile(r'^.\d+$')

API_ID = int(environ.get('API_ID', '25412293'))
API_HASH = environ.get('API_HASH', 'd58456be9931f3f6b8154a626fc1b3c6')
BOT_TOKEN = environ.get('BOT_TOKEN', '7405088923:AAFfF3pDlpvp2Ou5duXROhzOkRIsTxu0oEA')
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '5602400935').split()]
DATABASE_URI = environ.get('DATABASE_URI', "") 
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'PosterBot')
PORT = environ.get("PORT", "8080")