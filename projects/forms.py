from django import forms
from Users.models import Comment
from .models import *


class Addcommentinproject(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['user_id', 'project_id']
        widgets = {
            'comment': forms.TextInput(attrs={'cols': 80, 'rows': 20}),
        }


class Addproject(forms.ModelForm):
    class Meta:
        model = Projects
        # fields = "__all__"
        exclude = ['user_id', 'tags']


class Addimage(forms.ModelForm):
    class Meta:
        model = Images
        # fields = "__all__"
        exclude = ['project_id']


class addDonation(forms.ModelForm):
    class Meta:
        model = Donation
        exclude = ['user_id', 'project_id']


class addRating(forms.ModelForm):
    class Meta:
        model = Rating
        exclude = ['user_id', 'project_id']

    # class addTags(forms.ModelForm):
#          class Meta:
#             model = Tags
#             exclude= ['project_id']
