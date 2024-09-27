from django.db import models
from role.models import Role
from training_program.models import TrainingProgram  # Correct import

class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    training_programs = models.ManyToManyField(TrainingProgram, blank=True)  # Correct reference

    def __str__(self):
        return self.username
