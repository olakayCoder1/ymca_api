from django.contrib import admin

from account.models import Category, Church, IDCard, User, YouthGroup

# Register your models here.



admin.site.register(User)
admin.site.register(IDCard)
admin.site.register(Church)
admin.site.register(YouthGroup)
admin.site.register(Category)