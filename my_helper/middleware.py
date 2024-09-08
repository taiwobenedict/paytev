from django.shortcuts import redirect as r, render as rn
from django.urls import resolve as rv
from django import forms as f
from django.contrib import messages as m
from main.models import ActivationKeys as AK
import requests as rq
from .helpers import correct_url as cu, generate_key as gk, decrypt_key as dk

class ActivationForm(f.ModelForm):
    class Meta: 
        model = AK
        exclude = ('secret_key',)
        widgets = {
            'activation_key': f.TextInput({"class": "form-control", "placeholder": "Enter activation key"}),
            'activation_url': f.TextInput({"class": "form-control", "placeholder": "Enter public key"}),
        }
        help_texts = {
            'activation_url': "start with: https:// or http://"
        }

def simpleMiddleware(gr):
    def middleware(req):
        cuu = rv(req.path_info).url_name
        try:
            s = AK.objects.get(pk=1)
            sk = gk(s.activation_key, req.get_host())
            if sk != s.secret_key:
                if cuu != "base":
                    return r('base')
            else:
                if cuu == "base":
                    print(cuu)
                    return r('home')
        except AK.DoesNotExist:
            if cuu != "base":
                return r('base')
        res = gr(req)
        return res
    return middleware

def simple(req):
    frm = ActivationForm()
    if req.method == "POST":
        frm = ActivationForm(req.POST)
        if frm.is_valid():
            ak = frm.cleaned_data["activation_key"]
            pk = frm.cleaned_data['activation_url']
            try:
                au = cu(dk(ak, pk)) + "verify_domain_key/"
                d = req.get_host()
            except:
                m.error(req, "Invalid keys")
                return rn(req, 'base.html', {"form": frm})
            try:
                dt = rq.post(au, json={"activation_key": ak, "domain": d}).json()
                if dt["success"]:
                    sk = dt['secret_key']
                    obj, cr = AK.objects.update_or_create(
                        pk=1,
                        defaults={
                            'secret_key': sk,
                            'activation_key': ak,
                            'activation_url': pk,
                            'activated': True
                        }
                    )
                    return r('home')
                else:
                    m.error(req, dt['error'])
            except rq.exceptions.RequestException as re:
                m.error(req, "Error: Something went wrong!")
    return rn(req, 'base.html', {"form": frm})
