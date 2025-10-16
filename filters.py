from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class HistoryFilterForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by("username"), required=False, label="User"
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
