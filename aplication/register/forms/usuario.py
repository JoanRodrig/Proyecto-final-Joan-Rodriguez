from django.forms import ModelForm, ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from aplication.register.models import Usuario


class UserForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = [
            'first_name',
            'last_name',
            'username',
            'fecha_nacimiento',
            'sexo',
            'email',
        ]
        error_messages = {
            "email": {
                "unique": "Ya existe un usuario con este email.",
            },
        }
        widgets = {
            "first_name": forms.TextInput(attrs={
                "placeholder": "Value",
                "id": "id_nombres",
                "class": (
                    "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 "
                    "rounded-lg focus:ring-blue-500 focus:border-blue-500 "
                    "block w-full p-2.5 pr-12 dark:bg-principal "
                    "dark:border-gray-600 dark:placeholder-gray-400 "
                    "dark:text-gray-400 dark:focus:ring-blue-500 "
                    "dark:focus:border-blue-500 dark:shadow-sm-light"
                ),
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "Value",
                "id": "id_apellidos",
                "class": (
                    "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 "
                    "rounded-lg focus:ring-blue-500 focus:border-blue-500 "
                    "block w-full p-2.5 pr-12 dark:bg-principal "
                    "dark:border-gray-600 dark:placeholder-gray-400 "
                    "dark:text-gray-400 dark:focus:ring-blue-500 "
                    "dark:focus:border-blue-500 dark:shadow-sm-light"
                ),
            }),
            "username": forms.TextInput(attrs={
                "placeholder": "Value",
                "id": "id_username",
                "class": (
                    "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 "
                    "rounded-lg focus:ring-blue-500 focus:border-blue-500 "
                    "block w-full p-2.5 pr-12 dark:bg-principal "
                    "dark:border-gray-600 dark:placeholder-gray-400 "
                    "dark:text-gray-400 dark:focus:ring-blue-500 "
                    "dark:focus:border-blue-500 dark:shadow-sm-light"
                ),
            }),
            "fecha_nacimiento": forms.DateInput(attrs={
                "type": "date",
                "placeholder": "Value",
                "id": "id_fecha_nacimiento",
                "class": (
                    "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 "
                    "rounded-lg focus:ring-blue-500 focus:border-blue-500 "
                    "block w-full p-2.5 pr-12 dark:bg-principal "
                    "dark:border-gray-600 dark:placeholder-gray-400 "
                    "dark:text-gray-400 dark:focus:ring-blue-500 "
                    "dark:focus:border-blue-500 dark:shadow-sm-light"
                ),
            }),
            "sexo": forms.Select(attrs={
                "id": "id_sexo",
                "class": (
                    "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 "
                    "rounded-lg focus:ring-blue-500 focus:border-blue-500 "
                    "block w-full dark:bg-principal dark:border-gray-600 "
                    "dark:placeholder-gray-400 dark:text-gray-400 "
                    "dark:focus:ring-blue-500 dark:focus:border-blue-500 "
                    "dark:shadow-sm-light"
                ),
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Value",
                "id": "id_email",
                "class": (
                    "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 "
                    "rounded-lg focus:ring-blue-500 focus:border-blue-500 "
                    "block w-full p-2.5 pr-12 dark:bg-principal "
                    "dark:border-gray-600 dark:placeholder-gray-400 "
                    "dark:text-gray-400 dark:focus:ring-blue-500 "
                    "dark:focus:border-blue-500 dark:shadow-sm-light"
                ),
            }),
            "password1": forms.PasswordInput(attrs={
                "placeholder": "Value",
                "id": "id_password1",
                "class": (
                    "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 "
                    "rounded-lg focus:ring-blue-500 focus:border-blue-500 "
                    "block w-full p-2.5 pr-12 dark:bg-principal "
                    "dark:border-gray-600 dark:placeholder-gray-400 "
                    "dark:text-gray-400 dark:focus:ring-blue-500 "
                    "dark:focus:border-blue-500 dark:shadow-sm-light"
                ),
            }),
            "password2": forms.PasswordInput(attrs={
                "placeholder": "Value",
                "id": "id_password2",
                "class": (
                    "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 "
                    "rounded-lg focus:ring-blue-500 focus:border-blue-500 "
                    "block w-full p-2.5 pr-12 dark:bg-principal "
                    "dark:border-gray-600 dark:placeholder-gray-400 "
                    "dark:text-gray-400 dark:focus:ring-blue-500 "
                    "dark:focus:border-blue-500 dark:shadow-sm-light"
                ),
            }),
        }

    def clean_nombres(self):
        nombres = self.cleaned_data.get("first_name")
        if not nombres or len(nombres) < 2:
            raise ValidationError("El nombre debe tener al menos 2 carácter.")
        return nombres.upper()

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get("last_name")
        if not apellidos or len(apellidos) < 1:
            raise ValidationError("El apellido debe tener al menos 1 carácter.")
        return apellidos.upper()
