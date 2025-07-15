from datetime import timedelta
from .models import Task
from categories.models import Article_type_W_R_A_B, Site, Official_holiday, CustomHoliday
from django.db.models import Max

def get_valid_publish_date(task_type_wrab, site_name, writer):
    # الإجازات الرسمية والخاصة
    weekend = set(Official_holiday.objects.values_list('holiday_day', flat=True))
    custom_weekend = set(CustomHoliday.objects.filter(user=writer).values_list('date', flat=True))

    # النوع الحالي وحده الأقصى
    current_type = Article_type_W_R_A_B.objects.get(type=task_type_wrab)
    max_allowed = current_type.number_of_article

    # الأنواع المماثلة له في الحد الأقصى
    similar_types = Article_type_W_R_A_B.objects.filter(number_of_article=max_allowed)

    # بيانات الموقع
    site = Site.objects.get(name=site_name)
    site_start = site.start_date
    current_days_gap = site.number_of_days

    # آخر تاريخ لهذا الكاتب في نفس النوع على نفس الموقع
    last_used_date = Task.objects.filter(
        publish_site__name=site_name,
        writer=writer,
        article_type_W_R_A_B=current_type
    ).aggregate(Max('publish_date'))['publish_date__max'] or site_start

    # عدد المهام في هذا اليوم لنفس الكاتب ولنفس الحد الأقصى
    task_count = Task.objects.filter(
        writer=writer,
        publish_date=last_used_date,
        article_type_W_R_A_B__in=similar_types
    ).count()

    # فرق الأيام لأنواع المقالات في نفس اليوم
    previous_days_gaps = Site.objects.filter(
        task__writer=writer,
        task__publish_date=last_used_date,
        task__article_type_W_R_A_B__in=similar_types,
        name=site_name
    ).distinct().values_list('number_of_days', flat=True)

    # آخر تاريخ نشر على نفس الموقع لأي كاتب
    latest_site_date = Task.objects.filter(
        publish_site__name=site_name
    ).aggregate(Max('publish_date'))['publish_date__max'] or site_start

    # هل الكاتب تأخر عن الجدول؟
    is_outdated = (latest_site_date - last_used_date).days >= current_days_gap

    # الشرط: لو نفس الفاصل الزمني + لسه في مساحة + مش متأخر → استخدم نفس اليوم
    if (
        task_count < max_allowed and
        all(gap == current_days_gap for gap in previous_days_gaps) and
        not is_outdated
    ):
        return last_used_date

    # غير كده نشتغل بالمعادلة الجديدة
    new_date = latest_site_date + timedelta(days=current_days_gap)

    while new_date.weekday() in weekend or new_date in custom_weekend:
        new_date += timedelta(days=1)

    return new_date
