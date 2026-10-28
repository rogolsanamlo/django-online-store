from django import forms

from .models import PaymentType


class OrderForm(forms.Form):
    name = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'}),
        error_messages={'required': 'این فیلد نمی تواند خالی باشد'},
    )
    family = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی'}),
        error_messages={'required': 'این فیلد نمی تواند خالی باشد'},
    )
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل'}),
        required=False,
    )
    phone_number = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره تلفن'}),
        max_length=11,
        required=False,
    )
    address = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'آدرس', 'rows': '2'}),
        error_messages={'required': 'آدرس نمی تواند خالی باشد'},
    )
    description = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'توضیحات', 'rows': '4'}),
        required=False,
    )
    # queryset is evaluated lazily, so importing this module never hits the DB
    payment_type = forms.ModelChoiceField(
        label="",
        queryset=PaymentType.objects.all(),
        empty_label=None,
        widget=forms.RadioSelect(attrs={'form': 'checkout-form'}),
        error_messages={'required': 'روش پرداخت را انتخاب کنید'},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # make sure at least the default payment type exists on a fresh DB
        if not PaymentType.objects.exists():
            PaymentType.get_default()
