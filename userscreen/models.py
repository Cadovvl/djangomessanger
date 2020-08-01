from django.db import models

# Create your models here.

class User(models.Model):
    nickname = models.CharField(max_length=100)
    realname = models.CharField(max_length=200)

class Message(models.Model):
    text = models.CharField(max_length=400)
    date = models.DateField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='messages')
