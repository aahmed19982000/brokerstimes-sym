from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Company
from .forms import CompanyForm
import datetime
from django.db.models import Sum, Q
from accounts.decorators import role_required

from datetime import date


from datetime import date, timedelta

@role_required('manager')
def dashboard_company(request):
    companies = Company.objects.all()
    total_companies = companies.count()
    today = date.today()
    next_30_days = today + timedelta(days=30)
    
    # إحصائيات الشركات - باستخدام end_date
    active_companies = companies.filter(end_date__gte=today).count()
    expired_companies = companies.filter(end_date__lt=today).count()
    total_amount_paid = companies.aggregate(total=Sum('amount_paid'))['total'] or 0
    expired_soon = companies.filter(
        end_date__gte=today,
        end_date__lte=next_30_days
    ).count()
    
    # حساب النسب المئوية
    active_percentage = round((active_companies / total_companies * 100) if total_companies > 0 else 0, 1)
    expired_soon_percentage = round((expired_soon / total_companies * 100) if total_companies > 0 else 0, 1)
    expired_percentage = round((expired_companies / total_companies * 100) if total_companies > 0 else 0, 1)
    
    # متوسط المبلغ للشركة
    avg_amount_per_company = round((total_amount_paid / total_companies) if total_companies > 0 else 0, 2)
    
    # نسبة النمو
    growth_rate = round(min((total_companies / 10 * 100), 100) if total_companies > 5 else 0, 1)
    
    # تمرير آخر 5 شركات حسب created_at
    recent_companies = companies.order_by('-created_at')[:5]
    
    # إحصاءات إضافية
    companies_without_end_date = companies.filter(end_date__isnull=True).count()
    companies_with_contract = companies.filter(contract_duration__isnull=False).count()
    
    # الشركات المنشورة على مواقع
    sites_stats = []
    if companies.exists():
        # يمكنك إضافة إحصاءات حسب المواقع إذا أردت
        pass
    
    context = {
        'total_companies': total_companies,
        'active_companies': active_companies,
        'expired_companies': expired_companies,
        'total_amount_paid': total_amount_paid,
        'active_company': active_companies,  # للتوافق مع القالب
        'expired_company': expired_companies,  # للتوافق مع القالب
        'expired_soon': expired_soon,
        
        # النسب المئوية المحسوبة
        'active_percentage': active_percentage,
        'expired_soon_percentage': expired_soon_percentage,
        'expired_percentage': expired_percentage,
        
        # إحصائيات إضافية
        'avg_amount_per_company': avg_amount_per_company,
        'growth_rate': growth_rate,
        'companies_without_end_date': companies_without_end_date,
        'companies_with_contract': companies_with_contract,
        
        # الشركات الأخيرة
        'recent_companies': recent_companies,
        
        # تواريخ للمقارنة في القالب
        'today': today,
        'next_30_days': next_30_days,
    }
    return render(request, 'companies/dashboard_company.html', context)


@role_required('manager')
def company_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    # حساب الأيام المتبقية - صححت الخطأ الأول
    days_until_expiry = None
    if company.end_date:
        delta = company.end_date - date.today()
        days_until_expiry = max(0, delta.days)
    
    # مدة العقد - صححت العرض ليكون النص وليس الرقم
    contract_duration_display = "غير محدد"
    if company.contract_duration:
        # استخدم duration (النص) بدلاً من number_of_duration (الرقم)
        contract_duration_display = f"{company.contract_duration.duration}"
    
    # حالة الشركة
    status = "بدون تاريخ"
    status_class = "no-date"
    if company.end_date:
        if company.end_date < date.today():
            status = "منتهي"
            status_class = "expired"
        elif days_until_expiry and days_until_expiry <= 30:
            status = "ينتهي قريباً"
            status_class = "warning"
        else:
            status = "نشط"
            status_class = "active"
    
    context = {
        # الكائن الأساسي
        'company': company,
        
        # المتغيرات التي يحتاجها القالب
        'days_until_expiry': days_until_expiry,
        'contract_duration_display': contract_duration_display,
        'status': status,
        'status_class': status_class,
        'today': date.today(),
        # ملاحظة: days_until_expiry مكررة في القاموس - أزلت التكرار
    }
    
    return render(request, 'companies/company_details.html', context)


@role_required('manager')
def company_list(request):
    # 1. الحصول على جميع الشركات مرتبة حسب تاريخ الانتهاء (كما كان)
    companies = Company.objects.all().order_by('end_date')
    
    # 2. البحث (يبقى كما هو بدون تغيير)
    search_query = request.GET.get('search', '')
    if search_query:
        companies = companies.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(website__icontains=search_query)
        )
    
    # 3. فلتر الحالة الجديد (من select name="status")
    status = request.GET.get('status', '')
    today = datetime.date.today()
    
    if status:
        if status == 'active':
            # شرط: تاريخ الانتهاء >= اليوم أو بدون تاريخ
            companies = companies.filter(
                Q(end_date__gte=today) | Q(end_date__isnull=True)
            )
        elif status == 'expired':
            # شرط: تاريخ الانتهاء < اليوم
            companies = companies.filter(end_date__lt=today)
        elif status == 'expiring_soon':
            # شرط: ينتهي خلال 30 يوم
            soon_date = today + datetime.timedelta(days=30)
            companies = companies.filter(
                end_date__range=[today, soon_date]
            )
        elif status == 'no_date':
            # شرط: بدون تاريخ انتهاء
            companies = companies.filter(end_date__isnull=True)
    
    # 4. فلتر مدة العقد الجديد (من select name="duration")
    duration = request.GET.get('duration', '')
    if duration:
        companies = companies.filter(contract_duration_id=duration)
    
    # 5. فلتر الموقع الجديد (من select name="site")
    site = request.GET.get('site', '')
    if site:
        companies = companies.filter(site_puplished__id=site)
    
    # 6. فلتر تاريخ الإضافة (من input name="date_from" و "date_to")
    date_from = request.GET.get('date_from', '')
    if date_from:
        companies = companies.filter(created_at__date__gte=date_from)
    
    date_to = request.GET.get('date_to', '')
    if date_to:
        companies = companies.filter(created_at__date__lte=date_to)
    
    # 7. فلتر المبلغ (من input name="amount_min" و "amount_max")
    amount_min = request.GET.get('amount_min', '')
    if amount_min:
        try:
            companies = companies.filter(amount_paid__gte=float(amount_min))
        except (ValueError, TypeError):
            pass  # إذا كانت القيمة غير صحيحة، نتجاهل الفلتر
    
    amount_max = request.GET.get('amount_max', '')
    if amount_max:
        try:
            companies = companies.filter(amount_paid__lte=float(amount_max))
        except (ValueError, TypeError):
            pass  # إذا كانت القيمة غير صحيحة، نتجاهل الفلتر
    
    # 8. الإحصائيات (نفس المتغيرات بدون تغيير)
    active_companies = Company.objects.filter(
        Q(end_date__gte=today) | Q(end_date__isnull=True)
    ).count()
    
    expiered_companies = Company.objects.filter(
        end_date__lt=today
    ).count()
    
    total_amount = Company.objects.aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    soon_date = today + datetime.timedelta(days=30)
    expire_soon = Company.objects.filter(
        end_date__range=[today, soon_date]
    ).count()
    
    # 9. جلب البيانات اللازمة للفلترات في القالب
    from categories.models import contract_duration, Site
    durations = contract_duration.objects.all()  # للفلتر
    sites = Site.objects.all()  # للفلتر
    
    # 10. تحديد إذا كان هناك فلترات نشطة
    has_filters = any([
        status, duration, site, date_from, date_to, amount_min, amount_max
    ])
    
    # 11. إعداد السياق (نفس المتغيرات + الجديدة)
    context = {
        # المتغيرات الأصلية (بدون تغيير)
        'companies': companies,
        'active_companies': active_companies,
        'expiered_companies': expiered_companies,
        'search_query': search_query,
        'total_amount': total_amount,
        'expire_soon': expire_soon,
        
        # المتغيرات الجديدة للفلترات
        'durations': durations,  # لقائمة مدة العقد في select
        'sites': sites,  # لقائمة المواقع في select
        'has_filters': has_filters,  # لعرض قسم الفلاتر النشطة
    }
    
    return render(request, 'companies/company_list.html', context)


@role_required('manager')
def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            # ⚠️ **التغيير المهم هنا:**
            # القديم: form.save() ← يسبب مشاكل مع ManyToManyField
            # الجديد: استخدام commit=False ثم save_m2m()
            
            # 1. احفظ الكائن الأساسي (Company) بدون العلاقات
            company = form.save(commit=False)
            
            # 2. احفظ الكائن الأساسي في قاعدة البيانات
            company.save()
            
            # 3. ⚠️ **هذا هو الجزء المهم: احفظ علاقات ManyToManyField**
            form.save_m2m()
            
            messages.success(request, 'تمت إضافة الشركة بنجاح!')
            return redirect('company_list')
        else:
            messages.error(request, 'حدث خطأ أثناء إضافة الشركة. يرجى التحقق من البيانات المدخلة.')
    else:
        form = CompanyForm()

    return render(request, 'companies/add_company.html', {
        'form': form,
    })


@role_required('manager')
def company_edit(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الشركة بنجاح!')
            return redirect('company_list')
        else:
            messages.error(request, 'حدث خطأ أثناء تعديل الشركة. يرجى التحقق من البيانات المدخلة.')
    else:
        form = CompanyForm(instance=company)

    return render(request, 'companies/company_edit.html', {'form': form, 'company': company})

@role_required('manager')
def company_delete(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        company.delete()
        messages.success(request, 'تم حذف الشركة بنجاح!')
        return redirect('company_list')

    return render(request, 'companies/company_confirm_delete.html', {'company': company})