import re
import os
from os import environ, getenv

id_pattern = re.compile(r'^.\d+$')

API_ID = int(environ.get('API_ID', '20389440'))
API_HASH = environ.get('API_HASH', 'a1a06a18eb9153e9dbd447cfd5da2457')
BOT_TOKEN = environ.get('BOT_TOKEN', '7405088923:AAG3oNxF-pgHq4g_dCX6zdNlRwsek_VSoEk')
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '5602400935').split()]
DATABASE_URI = environ.get('DATABASE_URI', "") 
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'PosterBoot')
PORT = environ.get("PORT", "8080")