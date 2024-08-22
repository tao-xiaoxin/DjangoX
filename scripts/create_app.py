import os
import logging
from django.conf import settings
from application.settings import BASE_DIR

logger = logging.getLogger(__name__)


class DjangoAppCreator:
    """
    创建Django App，将其放在apps目录中
    """

    def __init__(self, app_name):
        """
        :param app_name: App名称
        """
        self.app_name = app_name
        self.app_path = os.path.join(settings.BASE_DIR, "apps", app_name)

    def create_app(self):
        """
        创建App
        """
        if os.path.exists(self.app_path):
            print(self.warning(f"App name: {self.app_name} already exists. Please choose another name!"))
            return False

        os.makedirs(self.app_path)
        self._create_init_file()
        self._create_migrations_directory()
        self._create_app_files()
        print(self.success(f"App name: {self.app_name} created successfully in the apps directory!"))
        return True

    @staticmethod
    def warning(message):
        """
        :param message: 警告信息
        """
        return f"\033[1;33m[WARNING] {message}\033[0m"

    @staticmethod
    def success(message):
        """
        :param message: 成功信息
        """
        return f"\033[1;32m{message}\033[0m"

    def _create_init_file(self):
        """
        创建__init__.py文件
        """
        open(os.path.join(self.app_path, "__init__.py"), 'a', encoding='UTF-8').close()

    def _create_migrations_directory(self):
        """
        创建migrations目录和__init__.py文件
        """
        migrations_path = os.path.join(self.app_path, "migrations")
        os.makedirs(migrations_path)
        open(os.path.join(migrations_path, "__init__.py"), 'a', encoding='UTF-8').close()

    def _create_app_files(self):
        """
        创建App文件
        """
        files_content = {
            "apps.py": self._get_apps_content(),
            "models.py": self._get_models_content(),
            "views.py": self._get_views_content(),
            "urls.py": self._get_urls_content(),
            "admin.py": self._get_admin_content(),
            "tests.py": self._get_tests_content(),
            "serializers.py": self._get_serializers_content(),
            "filters.py": self._get_filters_content()
        }

        for file_name, content in files_content.items():
            with open(os.path.join(self.app_path, file_name), 'w', encoding='UTF-8') as f:
                f.write(content)

    def _get_apps_content(self):
        return f"""from django.apps import AppConfig


class {self.app_name.capitalize()}Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'apps.{self.app_name}'


"""

    def _get_models_content(self):
        return """from django.db import models
from configs.config import table_prefix
from utils.models import CoreModel, BaseModel
"""

    def _get_views_content(self):
        return """from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from utils.validator import handle_serializer_validation
from utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from utils.common import get_parameter_dict, formatdatetime
from django.db.models import Q, F, Sum, Count
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from utils.pagination import CustomPagination
import logging

logger = logging.getLogger(__name__)

# Create your views here.
"""

    def _get_urls_content(self):
        return """from django.urls import path, re_path
from rest_framework import routers

url = routers.SimpleRouter()
# url.register(r'some_view', SomeViewSet)

urlpatterns = [
    # path('some_path/', SomeView.as_view(), name='some_name'),
]

urlpatterns += url.urls
"""

    def _get_admin_content(self):
        return """from django.contrib import admin

# Register your models here.
"""

    def _get_tests_content(self):
        return """from django.test import TestCase

# Create your tests here.
"""

    def _get_serializers_content(self):
        return """from rest_framework import serializers
from utils.serializers import CustomModelSerializer
from utils.validator import CustomValidationError
from .models import *

# Create your serializers here.
"""

    def _get_filters_content(self):
        return """import django_filters
from django_filters.rest_framework import FilterSet
from .models import *

# Create your filters here.
"""


def run(*args):
    if not args:
        print(DjangoAppCreator.warning(
            "Usage: python manage.py runscript create_app --script-args app_name1 [app_name2 ...]"))
        print("This script will create the app(s) in the 'apps' directory of your Django project.")
        return

    for app_name in args:
        creator = DjangoAppCreator(app_name)
        creator.create_app()
