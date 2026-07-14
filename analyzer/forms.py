from django import forms
from django.contrib.auth.models import User
from .models import Resume


class RegisterForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Password"
            }
        )
    )

    class Meta:

        model = User

        fields = [
            "first_name",
            "username",
            "email",
            "password"
        ]

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Full Name"
                }
            ),

            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Username"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email Address"
                }
            ),

        }


class ResumeForm(forms.ModelForm):

    job_description = forms.CharField(

        widget=forms.Textarea(

            attrs={

                "class": "form-control",

                "rows": 8,

                "placeholder": "Paste complete Job Description here..."

            }

        )

    )

    class Meta:

        model = Resume

        fields = ["resume"]

        widgets = {

            "resume": forms.ClearableFileInput(

                attrs={

                    "class": "form-control"

                }

            )

        }