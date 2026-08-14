from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label="Ism")
    last_name = forms.CharField(max_length=50, required=False, label="Familiya")
    phone_number = forms.CharField(max_length=20, required=False, label="Telefon raqami")
    role = forms.ChoiceField(
        choices=[
            (User.ROLE_USER, "Frilanser / Talaba / Masofadan ishlovchi"),
            (User.ROLE_BUSINESS_OWNER, "Biznes / Kovorking / Kafe egasi")
        ],
        initial=User.ROLE_USER,
        label="Foydalanish maqsadi"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'role')


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Foydalanuvchi nomi yoki Telefon", widget=forms.TextInput(attrs={'placeholder': 'Login yoki username'}))
    password = forms.CharField(label="Parol", widget=forms.PasswordInput(attrs={'placeholder': 'Parol'}))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'telegram_username', 'avatar', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }
