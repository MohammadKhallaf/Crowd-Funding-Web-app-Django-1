from django.contrib.auth.models import User
from django.core.validators import *

from Users.models import *


class Categories(models.Model):
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name_plural = "Categories"


class Tags(models.Model):
    tags = models.CharField(max_length=100)

    def __str__(self):
        return self.tags


class Projects(models.Model):

    title = models.CharField(max_length=100)
    details = models.TextField()
    total_target = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # image = models.ForeignKey('Images',on_delete=models.DO_NOTHING,null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.DO_NOTHING)
    tags = models.ManyToManyField(Tags)

    def __str__(self):
        return self.title


class Images(models.Model):
    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="Project_images")

    def __str__(self):
        return self.image.name


class Rating(models.Model):
    class Meta:
        unique_together = (('project_id', 'user_id'),)

    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=((1, 1), (2, 2), (3, 3), (4, 4), (5, 5)))

    def __str__(self):
        return str(self.rating)


class ProjectReport(models.Model):
    user_id = models.ForeignKey(User, unique=True, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.project_id)


class Choosen_by_Admin(models.Model):
    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.project_id)
