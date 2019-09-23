from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserInfo(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True,
                                related_name='info')
    points = models.IntegerField(default=0)

class TriviaQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.TextField()
    question = models.TextField()
    choice1 = models.TextField()
    choice2 = models.TextField()
    choice3 = models.TextField()
    choice4 = models.TextField()
    correctChoice = models.IntegerField()

class Player(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    game = models.ForeignKey('Game',null=True,on_delete=models.CASCADE)
    choice = models.IntegerField(default=None,null=True)
    score = models.IntegerField(default=0)
    next = models.BooleanField(default=False)

class Game(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.IntegerField(default=0)
    p1 = models.ForeignKey(Player,related_name='gamep1',on_delete=models.CASCADE)
    p2 = models.ForeignKey(Player,related_name='gamep2',default=None,null=True,on_delete=models.CASCADE)
    question = models.ForeignKey(TriviaQuestion,null=True,on_delete=models.SET_NULL)
    questionTime = models.IntegerField(default=0)
    winner = models.ForeignKey(Player,related_name='gamewinner',null=True,on_delete=models.CASCADE)

@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created:
        UserInfo.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_info(sender, instance, **kwargs):
    instance.info.save()

  

                            
