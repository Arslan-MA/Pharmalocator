from django.contrib.auth.forms import UserCreationForm, UserChangeForm, \
    PasswordChangeForm, AuthenticationForm
from django.urls import reverse_lazy
from django.shortcuts import redirect
from admin_app.models import *
from django import forms


class CustomUserAdminCreationForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'phone', 'is_staff', 'is_courier']
        labels = {
            'name': 'Имя пользователя',
            'email': 'Электронная почта',
            'phone': 'Номер телефона',
            'is_staff': 'Статус фармацевт',
            'is_courier': 'Статус курьер',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].label = 'Пароль'
        self.fields['password'].help_text = "Невозможно изменить чужой пароль"

    def clean(self):
        cleaned_data = super().clean()
        is_staff = cleaned_data.get("is_staff")
        is_courier = cleaned_data.get("is_courier")
        if is_staff and is_courier:
            raise forms.ValidationError("Пользователь не может быть одновременно фармацевтом и курьером.")
        return cleaned_data


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'photo', 'phone']
        labels = {
            'name': 'Имя пользователя',
            'email': 'Электронная почта',
            'photo': 'Фото профиля',
            'phone': 'Номер телефона',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        self.fields['name'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


class CustomUserAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Электронная почта'
        self.fields['password'].label = 'Пароль'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'photo', 'phone']
        labels = {
            'name': 'Имя пользователя',
            'email': 'Электронная почта',
            'photo': 'Фото профиля',
            'phone': 'Номер телефона',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.HiddenInput()
        self.fields['name'].help_text = None


class CustomUserPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = CustomUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Старый пароль'
        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password2'].label = 'Подтверждение нового пароля'
        self.fields['old_password'].help_text = None
        self.fields['new_password1'].help_text = None
        self.fields['new_password2'].help_text = None


class MedicineModelForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['title', 'photo', 'medicinal_category', 'type_medicine',
                  'age_category', 'description', 'price']
        labels = {
            'title': 'Название',
            'photo': 'Изображение',
            'medicinal_category': 'Категория лекарства',
            'type_medicine': 'Тип лекарства',
            'age_category': 'Возрастная категория',
            'description': 'Описание',
            'price': 'Цена',
        }


class PharmacyModelForm(forms.ModelForm):
    class Meta:
        model = Pharmacy
        fields = ['name', 'pharmacist', 'photo', 'phone', 'address']
        labels = {
            'name': 'Название',
            'pharmacist': 'Фармацевт',
            'photo': 'Логотип аптеки',
            'phone': 'Номер телефона',
            'address': 'Адрес'
        }


class MyPharmacyModelForm(forms.ModelForm):
    class Meta:
        model = Pharmacy
        fields = ['name', 'photo', 'phone', 'address']
        labels = {
            'name': 'Название',
            'photo': 'Логотип аптеки',
            'phone': 'Номер телефона',
            'address': 'Адрес'
        }


class MedicineCommentModelForm(forms.ModelForm):
    class Meta:
        model = MedicineComment
        fields = ('body', )
