import os

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    'users.auth.CustomBackend',
    # 'django.contrib.auth.backends.ModelBackend',
]

AUTH_API_BASE_URL = os.getenv('AUTH_API_BASE_URL')
AUTH_API_PORT = os.getenv('AUTH_API_PORT')

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
