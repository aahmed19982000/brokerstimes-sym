from django.db import models
from django.utils import timezone
from django.conf import settings

class Site(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الموقع")
    start_date = models.DateField(null=True, blank=True, verbose_name="تاريخ البدء")  
    number_of_days = models.PositiveIntegerField(verbose_name="عدد ايام الفارق")
    site_link = models.URLField(max_length=200, verbose_name="رابط الموقع")
   


    def __str__(self):  
        return self.name

class Article_type_U_N(models.Model):
    type = models.CharField(max_length=100, verbose_name="(تحديث ام جديد)نوع المقال")
    number_of_article = models.PositiveIntegerField(verbose_name="عدد المقالات المسموح بها")

    def __str__(self):
        return self.type

class Article_type_W_R_A_B(models.Model):
    type = models.CharField(max_length=100, verbose_name="(تحذير / تقييم/تعليمي/افضل شركات)نوع المقال")
    number_of_article = models.PositiveIntegerField(verbose_name="عدد المقالات المسموح بها")

    def __str__(self):
        return self.type

WEEKDAYS = [
    (5, 'السبت'),
]
class Official_holiday(models.Model):
    holiday_day = models.IntegerField(choices=WEEKDAYS, default=5, verbose_name="اليوم الرسمي للإجازة")  

class CustomHoliday(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="المستخدم")
    date = models.DateField(verbose_name="تاريخ الإجازة")
    reason = models.CharField(max_length=255, blank=True, null=True, verbose_name="سبب الإجازة (اختياري)")

    class Meta:
        verbose_name = "إجازة مخصصة"
        verbose_name_plural = "إجازات مخصصة"
        unique_together = ('user', 'date')  

    def __str__(self):
        return f"{self.user.username} - {self.date}"