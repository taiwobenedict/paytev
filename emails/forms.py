from django import forms

class BulkEmailForm(forms.Form):
    subject = forms.CharField(max_length=255)
    body = forms.CharField(widget=forms.Textarea)
