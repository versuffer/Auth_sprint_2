# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "debug_toolbar",
    'corsheaders',
    'movies.apps.MoviesConfig',
    'users.apps.UsersConfig',
]
