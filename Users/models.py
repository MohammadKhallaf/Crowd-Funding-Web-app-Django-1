from django.contrib.auth.models import User
from django.db import models

from projects.models import *

# Create your models here.
'''
    user model contains column:
        fname -> charfield
        lname -> charfield
        email -> emialfield
        password -> passwordfield
        phone -> mobilefield
        profile -> profilefield
'''


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=12, validators=[RegexValidator(regex='^01[0|1|2|5][0-9]{8}$',
                                                                       message='Phone must be start 010, 011, 012, 015 and all number contains 11 digits',
                                                                       code='invalid number')])
    birth = models.DateField(null=True)
    social_media = models.URLField()
    country = models.CharField(max_length=40)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', blank=True)

    def __str__(self):
        return f'{self.user.username} '

    # -----------------------------------------------------------------------------------------------------------------
    '''
        Donation model contains column:   
            user_id -> ForeignKey from table user
            project_id -> ForeignKey from table project using import
            amount_of_money -> FloatField
    '''


class Donation(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id = models.ForeignKey('projects.Projects', on_delete=models.CASCADE)
    amount_of_money = models.FloatField()

    def __str__(self):
        return "User Id" + str(self.user_id)


# -----------------------------------------------------------------------------------------------------------------
class Comment(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id = models.ForeignKey('projects.Projects', on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return "Comment Id" + str(self.user_id)


# -----------------------------------------------------------------------------------------------------------------
class Replay(models.Model):
    comment_id = models.ForeignKey('Comment', on_delete=models.CASCADE)
    replay = models.TextField()

    def __str__(self):
        return "Comment Id" + str(self.user_id)


# -----------------------------------------------------------------------------------------------------------------
class Reportno(models.Model):
    # class Meta:
    #     # unique_together = (('user_id', 'comment_id'),)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_id = models.ForeignKey('Comment', on_delete=models.CASCADE)

    def __str__(self):
        return "User Id" + str(self.user_id)
