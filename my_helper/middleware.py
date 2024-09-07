from django.shortcuts import redirect, render
from django.urls import resolve
from django import forms
from django.contrib import messages
from main.models import ActivationKeys
import requests
from .helpers import correct_url, generate_key, decrypt_key

class ActivationForm(forms.ModelForm):
    class Meta: 
        model = ActivationKeys
        exclude = ('secret_key',)
        widgets = {
            'activation_key': forms.TextInput({"class": "form-control", "placeholder": "Enter activation key"}),
            'activation_url': forms.TextInput({"class": "form-control", "placeholder": "Enter public key"}),
        }
        help_texts = {
            'activation_url': "start with: https:// or http://"
        }

def simpleMiddleware(get_response):
    def middleware(request):
        current_url = resolve(request.path_info).url_name
        
    
        try:
            site = ActivationKeys.objects.get(pk=1)
            stored_key = generate_key(site.activation_key, request.get_host())
            
            if stored_key != site.secret_key:
                
                if current_url != "base":
                    return redirect('base')
            else:
                if current_url == "base":
                    print(current_url)
                    return redirect('home')
                

        except ActivationKeys.DoesNotExist:
            if current_url != "base":
                    return redirect('base')
                
                
        response = get_response(request)
        return response
    
    return middleware


def simple(request):
    form = ActivationForm()

    
    if request.method == "POST":
        form = ActivationForm(request.POST)
        if form.is_valid():
            activation_key = form.cleaned_data["activation_key"]
            public_key = form.cleaned_data['activation_url']
            activation_url = correct_url(decrypt_key(activation_key, public_key))
            
            try:
                activation_url = correct_url(decrypt_key(activation_key, public_key)) + "verify_domain_key/"
                domain = request.get_host()
            except:
                 messages.error(request, "Invalid keys")
                
            
            try:
                data = requests.post(activation_url, json={"activation_key": activation_key, "domain": domain}).json()
                if data["success"]:
                    secret_key = data['secret_key']
                    
                    # Update or create the ActivationKeys object
                    obj, created = ActivationKeys.objects.update_or_create(
                        pk=1,
                        defaults={
                            'secret_key': secret_key,
                            'activation_key': activation_key,
                            'activation_url': activation_url,
                            'activated': True
                        }
                    )
                    return redirect('home')
                else:
                    messages.error(request, data['error'])
    
            except requests.exceptions.RequestException as req_err:
                messages.error(request, "Error: URL might be invalid or an internet error!")
    
    return render(request, 'base.html', {"form": form})
