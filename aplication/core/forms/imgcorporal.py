# forms.py
from django import forms
from aplication.core.models import ImagenCorporal

class ImagenCorporalForm(forms.ModelForm):
    class Meta:
        model = ImagenCorporal
        fields = ['imagen']
