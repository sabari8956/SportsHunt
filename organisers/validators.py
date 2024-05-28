from .models import *
from django.contrib import messages

def clean_querydict(querydict):
    return {k: v[-1] for k, v in querydict.lists()}

class OrganisationValidator:
    def __init__(self, req):
        self.req = req
        self.data = clean_querydict(req.POST)
        self.user = req.user
        
        
        
    
    def clean_org_name(self, org_name):
        self.data[org_name] = org_name.lower().replace(' ', '_')
        return True
    
    def clean_wh_num(self, wh_num):
        try:
            self.data[wh_num] = int(wh_num)
            return True

        except ValueError:
            messages.add_message(self.req, messages.ERROR, 'Invalid number')
            return False
    
    def validate_org_name(self, org_name):
        org_name = org_name.lower().replace(" ", "_")
        if org_name and Organisation.objects.filter(name=org_name).exists():
            print('org name exists')
            messages.add_message(self.req, messages.ERROR, 'Organisation name already exists.')
            return False
        return True    
    
    
    def validate_wh_num(self, wh_num):
        if wh_num.isdigit() and len(wh_num) == 10:
            return True
        else:
            messages.add_message(self.req, messages.ERROR, 'Invalid number')
            return False
        
    def save(self):
        org = Organisation(name=self.data.get('org_name'), wh_num=self.data.get('wh_num'), admin=self.user)
        org.save()
        self.req.session['organisation'] = org.id
        return org
    
    def clean_validate_save(self):
        clean_fns = [fn for fn in dir(self) if fn.startswith('clean_')]
        validate_fns = [fn for fn in dir(self) if fn.startswith('validate_')]

        for clean_fn in clean_fns:
            fn_call = getattr(self, clean_fn)
            _, key = clean_fn.split('_', 1)
            fn_data = self.data.get(key, None)
            if fn_data:
                fn_call(fn_data)
                
        for validate_fn in validate_fns:
            fn_call = getattr(self, validate_fn)
            _, key = validate_fn.split('_', 1)
            fn_data = self.data.get(key, None)
            if fn_data:
                if not fn_call(fn_data):
                    return False

        self.save()
        return True
        

        
        