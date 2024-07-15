from django.db import models
from utils.models import BaseModel
from application.settings import table_prefix
from utils.models import BaseModel
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Users(AbstractUser, BaseModel):
    IDENTITY_CHOICES = (
        (0, "超级管理员"),
        (1, "系统管理员"),
        (2, "前端用户"),

    )
    GENDER_CHOICES = (
        (0, "女"),
        (1, "男"),
    )

    user_name = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='用户账号',
                                 help_text="用户账号")
    email = models.EmailField(max_length=60, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    mobile = models.CharField(max_length=30, verbose_name="电话", null=True, blank=True, help_text="电话")
    avatar = models.CharField(max_length=200, verbose_name="头像", null=True, blank=True, help_text="头像")
    name = models.CharField(max_length=40, verbose_name="姓名", help_text="姓名")
    nickname = models.CharField(max_length=100, help_text="用户昵称", verbose_name="用户昵称", default="")
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, verbose_name="性别", null=True, blank=True,
                                      help_text="性别")
    # 自定义
    identity = models.SmallIntegerField(choices=IDENTITY_CHOICES, verbose_name="身份标识", null=True, blank=True,
                                        default=2, help_text="身份标识")

    class Meta:
        db_table = table_prefix + "users"
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)
