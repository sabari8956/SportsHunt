from django import forms
from .models import Organisation, Tournament

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


class TournamentForm(forms.Form):
    name = forms.CharField(max_length=100, label="Tournament Name")
    start_date = forms.DateField(label="Start Date" )
    end_date = forms.DateField(label="End Date")
    game = forms.ChoiceField(choices=[('Badminton', 'badminton'), ('Tennis', 'tennis')], label="Game")
    
    def clean_name(self):
        name = self.cleaned_data['name'].lower().replace(" ", "_")
        if name and Organisation.objects.filter(name=name).exists():
            raise forms.ValidationError("Tournament name already exists.")
        return name

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        if start_date:
            return start_date
        else:
            raise forms.ValidationError("Invalid Date")
    
    def clean_end_date(self):
        end_date = self.cleaned_data['end_date']
        if end_date:
            return end_date
        else:
            raise forms.ValidationError("Invalid Date")
        
    def save(self, org=None, commit=True):
        if not org:
            raise Exception("Organisation is required")
        
        org = Organisation.objects.get(id=org)
        tournament = Tournament(**self.cleaned_data, org=org)
        if commit:
            tournament.save()
        return tournament