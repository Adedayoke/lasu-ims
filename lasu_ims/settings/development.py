from .base import *
from decouple import config

DEBUG = config('DEBUG', default=True, cast=bool)
