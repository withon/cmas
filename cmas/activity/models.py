from django.db import models
from django.conf import settings

# Create your models here.


# class User(models.Model):
#     number = models.CharField(max_length=20, unique=True)
#     passwd_hash = models.CharField(max_length=100, default='123456')
#     name = models.CharField(max_length=50)
#     sex = models.CharField(max_length=2)
#     power = models.IntegerField(default=1)

#     def __str__(self):
#         return "<id: %s num: %s>" % (self.pk, self.number)


class Activity(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField(max_length=5000)
    stime = models.DateTimeField()
    ftime = models.DateTimeField()
    ctime = models.DateTimeField(auto_now_add=True)
    rtime = models.DateTimeField(auto_now=True)
    act_type = models.CharField(max_length=10)
    max_num = models.IntegerField()
    point = models.FloatField(default=0)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, to_field='id', on_delete=models.DO_NOTHING)
    is_freeze = models.BooleanField(default=False)

    class Meta:
        ordering = ['-rtime']

    def __str__(self):
        return "<title: %s>" % self.title


class Registration(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, to_field='id', on_delete=models.DO_NOTHING)
    act_id = models.ForeignKey(
        'Activity', to_field='id', on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ['-time']
        unique_together = (
            ('user_id', 'act_id'),
        )

    def __str__(self):
        return "<uid: %s aid: %s>" % (self.user_id, self.act_id)


class Sysnotice(models.Model):
    content = models.CharField(max_length=500)
    time = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, to_field='id', on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ['-time']

    def __str__(self):
        return "<sysno uid: %s>" % self.user_id
