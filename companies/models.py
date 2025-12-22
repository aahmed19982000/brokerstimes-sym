from django.db import models
from django.utils import timezone
from datetime import timedelta
from categories.models import Site , contract_details , contract_duration

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم الشركة")
    email = models.CharField(max_length=500, verbose_name="عنوان البريد الإلكتروني", blank=True, null=True)
    website = models.URLField(max_length=500, verbose_name="موقع الشركة", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    end_date = models.DateField(verbose_name="تاريخ الانتهاء", blank=True, null=True)
    contract_duration = models.ForeignKey(contract_duration, on_delete=models.CASCADE, verbose_name="مدة العقد", blank=True, null=True)
    site_puplished = models.ManyToManyField(Site, verbose_name="الموقع المنشور عليه", blank=True )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ المدفوع", blank=True, null=True)
    nots = models.TextField(verbose_name="ملاحظات", blank=True, null=True)
    contract_details= models.ManyToManyField(contract_details,  verbose_name="تفاصيل العقد", blank=True )

    def save(self, *args, **kwargs):
        # إذا كان هناك مدة عقد ولم يتم تحديد تاريخ انتهاء
        if self.contract_duration and not self.end_date:
            try:
                # تحويل المدة إلى عدد أيام
                days_to_add = int(self.contract_duration.number_of_duration * 365)
                
                # حساب تاريخ الانتهاء
                if self.created_at:
                    self.end_date = self.created_at.date() + timedelta(days=days_to_add)
                else:
                    self.end_date = timezone.now().date() + timedelta(days=days_to_add)
            except (ValueError, TypeError):
                # إذا كانت المدة غير رقمية
                pass
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


    