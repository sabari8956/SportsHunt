from django import forms
from .models import Organisation

class OrganaisationForm(forms.Form):
    name = forms.CharField(max_length=100, label="Organisation Name")
    mail = forms.EmailField(label="Email")
    wh_num = forms.CharField(max_length=10, label="Whatsapp Number")
    
    def clean_name(self):
        name = self.cleaned_data['name'].lower().replace(" ", "_")
        if name and Organisation.objects.filter(name=name).exists():
            raise forms.ValidationError("Organisation name already exists.")
        return name
    
    def clean_wh_num(self):
        wh_num = self.cleaned_data['wh_num']
        if wh_num.isdigit() and len(wh_num) == 10:
            return wh_num
        else:
            raise forms.ValidationError("Invalid number")
        
    
    def save(self, admin=None, commit=True):
        if not admin:
            raise Exception("Admin is required")

        org = Organisation(**self.cleaned_data, admin=admin)
        if commit:
            org.save()
        return org
