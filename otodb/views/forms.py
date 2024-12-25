from django import forms

from otodb.models import MediaSong, MediaWork, TagMain, WorkSource

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)

class ManualWorkForm(forms.ModelForm):
    class Meta:
        model = MediaWork
        fields = ['title', 'description', 'rating', 'tags']

class ManualSourceForm(forms.ModelForm):
    class Meta:
        model = WorkSource
        fields = ['media', 'url', 'published_date', 'work_origin', 'work_status', 'work_width', 'work_height']

class WorkForm(forms.Form):
    link = forms.CharField(label='Link', required=True)
