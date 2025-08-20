from pathlib import Path
import os
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url


from environ import Env
env = Env()
Env.read_env()
ENVIRONMENT = env('ENVIRONMENT', default='production')
USE_CLOUDINARY = env.bool('USE_CLOUDINARY', default=False)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == 'development':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ["*"]


# Flutterwave secret key
if ENVIRONMENT == 'development':
    FLUTTERWAVE_SECRET_KEY = env('FLUTTERWAVE_SECRET_KEY_TEST')
    FLUTTERWAVE_PUBLIC_KEY = env('FLUTTERWAVE_PUBLIC_KEY_TEST')
else:
    FLUTTERWAVE_SECRET_KEY = env('FLUTTERWAVE_SECRET_KEY_LIVE')
    FLUTTERWAVE_PUBLIC_KEY = env('FLUTTERWAVE_PUBLIC_KEY_LIVE')
NOTIFY_EVENTS_SOURCE = env('NOTIFY_EVENTS_SOURCE')


# CORS settings 
CORS_ALLOWED_ORIGINS = [
    "https://checkout.flutterwave.com",
    "https://api.flutterwave.com",
]


# Security settings
SECURE_CROSS_ORIGIN_OPENER_POLICY = None 

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "django.contrib.humanize",
    'main.apps.MainConfig',  # Main app for the quick cart
    'corsheaders',  # CORS headers for API requests
    'administration',  # Administration app for managing the quick cart
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    "whitenoise.middleware.WhiteNoiseMiddleware",
     
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    "corsheaders.middleware.CorsMiddleware",
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom middleware for visitor notifications
    "main.middleware.VisitorNotificationMiddleware"
]

#MIDDLEWARE += ["main.middleware.VisitorNotificationMiddleware"]

ROOT_URLCONF = 'a_quickcart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'a_quickcart.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

POSTGRESS_LOCALLY = True
if ENVIRONMENT == 'production' or POSTGRESS_LOCALLY == True:
        DATABASES['default'] = dj_database_url.parse(env('DATABASE_URL'))


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


EMAIL_BACKEND ='django.core.mail.backends.console.EmailBackend'




# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# For Session based logout 
# Auto logout users after 30 minutes (1800 seconds) of inactivity
SESSION_COOKIE_AGE = 1800  

# Refresh session expiry time on every request
SESSION_SAVE_EVERY_REQUEST = True


# Add authentication URLs
LOGIN_URL = '/owner/login/'
LOGIN_REDIRECT_URL = '/owner/dashboard/'
LOGOUT_REDIRECT_URL = '/owner/login/'


# Media files (User-uploaded content)
if ENVIRONMENT == 'production' or USE_CLOUDINARY:
    # Cloudinary configuration
    CLOUDINARY = {
        'cloud_name': env('CLOUDINARY_CLOUD_NAME'),
        'api_key': env('CLOUDINARY_API_KEY'),
        'api_secret': env('CLOUDINARY_API_SECRET'),
    }

    cloudinary.config(**CLOUDINARY)

    # Media URL for Cloudinary
    MEDIA_URL = f"https://res.cloudinary.com/{CLOUDINARY['cloud_name']}/"
else:
    # Local media setup
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/



STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')#STATIC_ROOT = '/var/www/static'
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
