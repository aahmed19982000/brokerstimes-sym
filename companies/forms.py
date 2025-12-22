from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'email', 'website', 'end_date', 
            'contract_duration', 'site_puplished', 
            'amount_paid', 'nots', 'contract_details'
        ]
        
        # ⚠️ التغيير المهم: تغيير widget لحقول ManyToManyField
        widgets = {
            # الحقول العادية تبقى كما هي
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contract_duration': forms.Select(attrs={'class': 'form-control'}),
            
            # ✅ التغيير: SelectMultiple بدلاً من Select
            'site_puplished': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'multiple': 'multiple',  # ⚠️ هذا مهم
                'style': 'min-height: 120px;'
            }),
            
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'nots': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            
            # ✅ نفس التغيير لـ contract_details
            'contract_details': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'multiple': 'multiple',
                'style': 'min-height: 120px;'
            }),
        }
        
        # نصوص المساعدة للمستخدم
        help_texts = {
            'site_puplished': 'اضغط على Ctrl (أو Cmd في Mac) لتحديد خيارات متعددة',
            'contract_details': 'اضغط على Ctrl (أو Cmd في Mac) لتحديد خيارات متعددة',
        }