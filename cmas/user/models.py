from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=30, default='未知', verbose_name='姓名')

    class Meta(AbstractUser.Meta):
        pass
