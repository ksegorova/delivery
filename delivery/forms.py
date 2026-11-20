import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, DeliveryZone

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Электронная почта')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {'username': 'Имя пользователя'}

class CheckoutForm(forms.Form):
    address = forms.CharField(label='Адрес доставки', max_length=250, widget=forms.TextInput(attrs={'placeholder':'Улица, дом, квартира'}))
    zone = forms.ModelChoiceField(label='Зона доставки', queryset=DeliveryZone.objects.all())
    phone = forms.CharField(label='Телефон', max_length=20, widget=forms.TextInput(attrs={'placeholder':'+7 900 000-00-00'}))
    comment = forms.CharField(label='Комментарий курьеру', required=False, max_length=300, widget=forms.Textarea(attrs={'rows':3}))
    def clean_phone(self):
        value = self.cleaned_data['phone']
        if len(re.sub(r'\D', '', value)) < 10:
            raise forms.ValidationError('Введите корректный номер телефона.')
        return value
