# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w2#@_!5tgn3i@83di_itgr-r1pm4#rw&bd7^t0%j*!x5ja7=-v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
