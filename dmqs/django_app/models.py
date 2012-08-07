from django.db import models

class Dog(models.Model):
    name = models.CharField(null=False, blank=False, max_length=150)

class BestFriend(models.Model):
    person   = models.ForeignKey('Friend')
    nickname = models.CharField(max_length=100, null=True)

class Friendship(models.Model):
    best_friend1 = models.ForeignKey('BestFriend', related_name="reverse_friend")
    best_friend2 = models.ForeignKey('Friend')
    since        = models.DateField(null=False)

class Friend(models.Model):
    name         = models.CharField(null=False, blank=False, max_length=150)

    dog          = models.ForeignKey(Dog, null=True)
    other_dog    = models.OneToOneField(Dog, null=True, related_name="other")

    friends      = models.ManyToManyField('self', null=True)
    best_friends = models.ManyToManyField(BestFriend,
                                          through=Friendship, null=True,
                                          related_name="friendship")
