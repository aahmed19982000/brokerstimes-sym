from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'website', 'created_at', 'end_date',   'amount_paid', 'nots')
    search_fields = ('name', 'email')
    list_filter = ('created_at', 'end_date')

    # التحكم بالحقول اللي تظهر في نموذج الإضافة والتعديل
    fields = ('name', 'email', 'website',  'end_date',   'amount_paid', 'nots')
