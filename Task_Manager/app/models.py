from django.db import models
from django.contrib.auth.models import User

class TaskModel(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")



