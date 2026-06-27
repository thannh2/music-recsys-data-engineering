import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KAFKA_BROKER = 'localhost:9092'

TOPICS = {
    'interactions': 'music_interactions',
    'users': 'users_metadata',
    'albums': 'albums_metadata'
}

DATA_FILES = {
    'interactions': os.path.join(BASE_DIR, 'data', 'lfm1b-albums.inter'),
    'users': os.path.join(BASE_DIR, 'data', 'lfm1b-albums.user'),
    'albums': os.path.join(BASE_DIR, 'data', 'lfm1b-albums.item')
}