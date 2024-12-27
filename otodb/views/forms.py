from django import forms

from otodb.models import MediaSong, MediaWork, TagMain, WorkSource, Pool, PoolItem

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)

class WorkForm(forms.ModelForm):
    class Meta:
        model = MediaWork
        fields = ['title', 'description', 'rating', 'thumbnail']

class ManualSourceForm(forms.ModelForm):
    class Meta:
        model = WorkSource
        fields = ['media', 'url', 'published_date', 'work_origin', 'work_status', 'work_width', 'work_height']

class SourceSiteForm(forms.Form):
    link = forms.CharField(label='Link', required=True)
    official = forms.BooleanField(label='Is this an official upload?', required=False)

class ListForm(forms.ModelForm):
    class Meta:
        model = Pool
        fields = ['name', 'description', 'status']
