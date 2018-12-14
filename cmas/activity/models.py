from django.db import models

# Create your models here.


class User(models.Model):
    number = models.CharField(max_length=20, unique=True)
    passwd_hash = models.CharField(max_length=100, default='123456')
    name = models.CharField(max_length=50)
    sex = models.CharField(max_length=2)
    power = models.IntegerField(default=1)

    def __str__(self):
        return "<id: %d num: %s>" % self.pk % self.number


class Activity(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField(max_length=5000)
    stime = models.DateTimeField()
    ftime = models.DateTimeField()
    ctime = models.DateTimeField(auto_now_add=True)
    rtime = models.DateTimeField(auto_now=True)
    act_type = models.CharField(max_length=10)
    user_id = models.ForeignKey(
        'User', to_field='id', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "<title: %s>" % self.title


class Registration(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(
        'User', to_field='id', on_delete=models.DO_NOTHING)
    act_id = models.ForeignKey(
        'Activity', to_field='id', on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (
            ('user_id', 'act_id'),
        )

    def __str__(self):
        return "<uid: %d aid: %d>" % self.user_id % self.act_id


class Mnotice(models.Model):
    title = models.CharField(max_length=20)
    content = models.CharField(max_length=200)
    time = models.DateTimeField(auto_now_add=True)
    is_delete = models.IntegerField(default=0)
    user_id = models.ForeignKey(
        'User', to_field='id', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "<uid: %d title: %s>" % self.user_id % self.title


class Sysnotice(models.Model):
    content = models.CharField(max_length=500)
    time = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(
        'User', to_field='id', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "<sysno uid: %d>" % self.user_id
