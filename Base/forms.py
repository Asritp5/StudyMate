from django.forms import ModelForm
from .models import Room,User
from django.contrib.auth.forms import UserCreationForm

class RoomForm(ModelForm):
    class Meta:
        model=Room
        fields='__all__'
        exclude=['host','participants']

class MyUserCreationForm(UserCreationForm): #register new user
    class Meta:
        model=User
        fields=['name','email','password1','password2','bio','avatar']

class MyUserUpdationForm(ModelForm):
    class Meta:
        model=User
        fields=['name','email','bio','avatar']
        

    def __init__(self, *args, **kwargs):
        super(MyUserUpdationForm, self).__init__(*args, **kwargs)
        self.fields['email'].disabled = True    
