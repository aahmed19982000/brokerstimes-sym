from django.db import models
from django.conf import settings
from  categories.models import Site , Article_type_U_N ,Article_type_W_R_A_B
STATUS_CHOICES = [  ('in_progress', '⏳ جاري العمل'),
    ('upload', 'تم الرفع'),
    ('publish', 'تم النشر'),
    ('done', '✅ مكتملة'), ]

class Task(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="الكاتب") 
    article_title = models.CharField(max_length=255, verbose_name="المقال")
    article_details = models.TextField(verbose_name="تفاصيل المقال")
    article_link = models.URLField(max_length=500, verbose_name="رابط المقال", blank=True, null=True)
    publish_site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="موقع النشر")
    publish_date = models.DateField(verbose_name="تاريخ النشر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    article_type_W_R_A_B = models.ForeignKey(Article_type_W_R_A_B, on_delete=models.CASCADE, verbose_name=" نوع المقال( تحذير / تقييم/تعليمي/افضل شركات)",null=True, blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='in_progress',verbose_name='حالة المهمة')

    def __str__(self):
        return self.article_title
