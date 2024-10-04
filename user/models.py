from django.db import models
from django.contrib.auth.models import User
from role.models import Role

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role.name if self.role else 'No Role'}"

