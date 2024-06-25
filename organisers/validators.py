from .models import *
from django.contrib import messages
from datetime import datetime, timedelta
import re

def clean_querydict(querydict):
    return {k: v[-1] for k, v in querydict.lists()}

class OrganisationValidator:
    def __init__(self, req):
        self.req = req
        self.data = clean_querydict(req.POST)
        self.user = req.user
        self.errors = []

    def clean_and_validate_org_name(self, org_name):
        if not org_name.strip():
            self.errors.append('Enter a org name.')
            return False
        org_name = org_name.lower().replace(" ", "_")
        self.data['org_name'] = org_name

        if org_name and Organisation.objects.filter(name=org_name).exists():
            self.errors.append('Organisation name already exists.')
            return False

        return True

    def clean_and_validate_wh_num(self, wh_num):
        if not wh_num.strip():
            self.errors.append('Enter a number.')
            return False
        try:
            self.data['wh_num'] = int(wh_num)
        except ValueError:
            self.errors.append('Invalid number')
            return False

        if not (wh_num.isdigit() and len(wh_num) == 10):
            self.errors.append('Invalid number')
            return False

        return True

    def save(self):
        if self.errors:
            for error in self.errors:
                messages.add_message(self.req, messages.ERROR, error)
            return False

        org = Organisation(name=self.data.get('org_name'), wh_num=self.data.get('wh_num'), admin=self.user)
        org.save()
        self.req.session['organisation'] = org.id
        return org

    def clean_validate_save(self):
        clean_and_validate_fns = [fn for fn in dir(self) if fn.startswith('clean_and_validate_')]

        for fn_name in clean_and_validate_fns:
            fn_call = getattr(self, fn_name)
            _, key = fn_name.split('_', 1)
            fn_data = self.data.get(key, None)

            if fn_data and not fn_call(fn_data):
                return False

        return self.save()
    


class TournamentValidator:
    def __init__(self, req):
        self.req = req
        self.data = clean_querydict(req.POST)
        print(self.data)
        self.data['dates'] = [self.data.get('start_date', None), self.data.get('end_date', None)]
        self.user = req.user
        self.errors = []

    def clean_and_validate_tournament_name(self, tournament_name):
        if not tournament_name.strip():
            self.errors.append('Enter a tournament name.')
            return False
        self.data['tournament_name'] = tournament_name.strip().lower().replace(" ", "_")
        if tournament_name and Tournament.objects.filter(name=tournament_name).exists():
            self.errors.append('Tournament name already exists.')
            return False
        return True

    def clean_and_validate_game(self, game):        
        if not game:
            self.errors.append('Game not selected')
            return False
        
        if not Game.objects.filter(id=game).exists():
            self.errors.append('Invalid game')
            return False
        
        self.data['game'] = game
        return True
    
    def clean_and_validate_phone_number(self, phone_number):
        if not phone_number.strip():
            self.errors.append('Enter a number.')
            return False
        try:
            self.data['phone_number'] = int(phone_number)
        except ValueError:
            self.errors.append('Invalid number')
            return False

        if not (phone_number.isdigit() and len(phone_number) == 10):
            self.errors.append('Invalid number')
            return False

        return True
    

    def clean_and_validate_venue(self, venue):
        if not venue.strip():
            self.errors.append('Enter a venue address.')
            return False
        self.data['venue'] = venue.strip()
        if len(venue) > 1024:
            self.errors.append('Venue name too long. Max 1024 characters.')
            return False
        return True

    def clean_and_validate_venue_link(self, venue_link):
        google_maps_regex = r'^https?:\/\/(?:www\.|maps\.app\.)?(?:google\.com\/maps\/|goo\.gl\/)\S*$'
        if not re.match(google_maps_regex, venue_link):
            self.errors.append('Invalid Google Maps link')
            return False

        self.data['venue_link'] = venue_link
        return True

    def clean_and_validate_dates(self, dates):
        if not dates:
            self.errors.append('Start and end dates not provided')
            return False
        start_date, end_date = dates
        if not start_date or not end_date:
            self.errors.append('Start or end dates not provided')
            return False
        print(f'validating {start_date} and {end_date} - {dates}')
        try:
            start_date = datetime.strptime(start_date, '%d/%m/%Y')
            end_date = datetime.strptime(end_date, '%d/%m/%Y')
        except ValueError:
            self.errors.append('Invalid date format. Use dd/mm/yyyy')
            return False

        if start_date > end_date:
            self.errors.append('Start date cannot be later than end date')
            return False
        
        if start_date < datetime.now() - timedelta(days=1):
            self.errors.append('Start date cannot be before today')
            return False
        

        self.data['start_date'] = start_date
        self.data['end_date'] = end_date
        return True

    def save(self):
        if self.errors:
            for error in self.errors:
                print(error)
                messages.add_message(self.req, messages.ERROR, error)
            return False

        tournament = Tournament(
            name=self.data.get('tournament_name'),
            venue=self.data.get('venue'),
            venue_link=self.data.get('venue_link'),
            start_date=self.data.get('start_date'),
            end_date=self.data.get('end_date'),
            org= Organisation.objects.get(id= self.req.session['organisation']),
        )
        tournament.save()
        return tournament

    def clean_validate_save(self):
        clean_and_validate_fns = [fn for fn in dir(self) if fn.startswith('clean_and_validate_')]
        print(clean_and_validate_fns)
        for fn_name in clean_and_validate_fns:
            fn_call = getattr(self, fn_name)
            _, key = fn_name.split('clean_and_validate_', 1)
            print(key)
            fn_data = self.data.get(key, None)
            if fn_data:
                fn_call(fn_data)
            
        return self.save()
 
 
 
class CategoryValidator:
    def __init__(self, req, tournament_name):
        self.req = req
        self.data = clean_querydict(req.POST)
        self.user = req.user
        self.errors = []
        self.tournament_name = tournament_name
        
        self.tournament_instance = Tournament.objects.get(name= tournament_name)
        self.all_categories= [category.catagory_type for category in self.tournament_instance.categories.all()]
        
    def clean_and_validate_category_type(self, category_type):
        if not category_type.strip():
            self.errors.append('Enter a category type.')
            return False
        self.data['category_type'] = category_type.strip().upper().replace(" ", "_")
        if self.data['category_type'] in self.all_categories:
            self.errors.append('Category already exists.')
            return False
        return True
    
    def clean_and_validate_details(self, details):
        self.data['details'] = details.strip()
        if not self.data['details']:
            self.errors.append('Details not provided')
            return False
        
        if len(details) > 254:
            self.errors.append('Details too long. Max 254 characters.')
            return False
        return True
    
    def clean_and_validate_max_age(self, max_age):
        if not max_age.strip():
            self.errors.append('Enter a age.')
            return False
        try:
            self.data['max_age'] = int(max_age)
        except ValueError:
            self.errors.append('Invalid age')
            return False
        return True
    
    def clean_and_validate_price(self, price):
        if not price.strip():
            self.errors.append('Set a price.')
            return False
        try:
            self.data['price'] = int(price)
        except ValueError:
            self.errors.append('Invalid price')
            return False
        return True
    
    def clean_and_validate_fixture_type(self, fixture_type):
        self.data['fixture_type'] = fixture_type.strip()
        if fixture_type.strip() != 'knockout':
            self.errors.append(f'{fixture_type} not supported Yet')
            return False
        return True
    
    
    def save(self):
        if self.errors:
            for error in self.errors:
                messages.add_message(self.req, messages.ERROR, error)
            return False

        category = Category(
            catagory_type=self.data.get('category_type'),
            details=self.data.get('details'),
            max_age=self.data.get('max_age'),
            price=self.data.get('price'),
            # fixture=self.data.get('fixture_type'),
            tournament=self.tournament_instance,
        )
        category.save()
        self.tournament_instance.categories.add(category)
        self.tournament_instance.save()
        
        if self.data.get('more_category'):
            messages.add_message(self.req, messages.INFO, f'Category {self.data.get('category_type')} created successfully')
            return False
        return category
    
    
    def clean_validate_save(self):
        clean_and_validate_fns = [fn for fn in dir(self) if fn.startswith('clean_and_validate_')]
        print(clean_and_validate_fns)
        for fn_name in clean_and_validate_fns:
            fn_call = getattr(self, fn_name)
            _, key = fn_name.split('clean_and_validate_', 1)
            print(key)
            fn_data = self.data.get(key, None)
            if fn_data:
                fn_call(fn_data)
            
        return self.save()
 

    