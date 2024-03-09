from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Organisation)
admin.site.register(Tournament)
admin.site.register(Category)
admin.site.register(Game)
admin.site.register(Team)
admin.site.register(Match)