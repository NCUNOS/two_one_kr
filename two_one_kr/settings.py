"""
Django settings for two_one_kr project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!bf0xhp!^yxnbqq)k)6(sg01wshuh%jcpyrjvrvvhy7wmq!)y+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'spider',
    'squirrel',
    'deer',
    'man',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mongoengine.django.mongo_auth',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'two_one_kr.urls'

WSGI_APPLICATION = 'two_one_kr.wsgi.application'


# Database
# For MongoDB
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

import mongoengine
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'twoonekr'
    },
}

SESSION_ENGINE = 'mongoengine.django.sessions' # optional

_MONGODB_USER = 'dontfailmeadmin'
_MONGODB_PASSWD = ''
_MONGODB_HOST = 'localhost'
_MONGODB_NAME = 'two_one_kr'
_MONGODB_DATABASE_HOST = \
    'mongodb://%s:%s@%s/%s' \
    % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_NAME)

mongoengine.connect(_MONGODB_NAME, host=_MONGODB_DATABASE_HOST)

# MONGODB AUTH
AUTHENTICATION_BACKENDS = (
    'mongoengine.django.auth.MongoEngineBackend',
)

AUTH_USER_MODEL = 'mongo_auth.MongoUser'

MONGOENGINE_USER_DOCUMENT = 'squirrel.models.User'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
