from dataclasses import field
from statistics import mode
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CreateUserCustomer(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
            