from django.contrib import admin
from .models import Site, Article_type_U_N ,Article_type_W_R_A_B, Official_holiday, CustomHoliday
@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name','number_of_days','start_date','site_link']

@admin.register(Article_type_U_N)
class Article_type_U_NAdmin(admin.ModelAdmin):
    list_display = ['type','number_of_article']

@admin.register(Article_type_W_R_A_B)
class Article_type_W_R_A_BAdmin(admin.ModelAdmin):
    list_display = ['type','number_of_article']

@admin.register(Official_holiday)
class Official_holidayAdmin(admin.ModelAdmin):
    list_display = ['holiday_day']

@admin.register(CustomHoliday)
class CustomHolidayAdmin(admin.ModelAdmin):
    list_display = ['user','reason','date']