from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import login_required 
from accounts.decorators import role_required
from accounts.models import Notification
from django.contrib.auth import get_user_model
from .utils import get_valid_publish_date 
from categories.models import Site
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from services.veryfction import url_form_sitemap_html

def get_status_label(code):
    return {
        'in_progress': '⏳ جاري العمل',
        'upload': '📤 تم الرفع',
        'publish': '📢 تم النشر',
        'done': '✅ مكتملة'
    }.get(code, code)

#وظيفة انشاء المهمام وعرضها 
@role_required('manager')

def task_list(request):
    tasks = Task.objects.all().order_by('-publish_date')
    form = None

    notifications = Notification.objects.filter(user=request.user, is_deleted=False).order_by('-created_at')[:10]
     # ✅ الحصول على بيانات الفلترة من GET
    writer_filter = request.GET.get('writer')
    status_filter = request.GET.get('status')
    site_filter = request.GET.get('site')
    search_query = request.GET.get('q')   

    if writer_filter:
     tasks = tasks.filter(writer_id=writer_filter)

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if site_filter:
        tasks = tasks.filter(publish_site__id=site_filter)

    if search_query:
        tasks = tasks.filter(
             Q(article_title__icontains=search_query) |
             Q(article_details__icontains=search_query) |
             Q(writer__username__icontains=search_query) |
             Q(writer__first_name__icontains=search_query) |
             Q(writer__last_name__icontains=search_query) |
             Q(article_type_W_R_A_B__type__icontains=search_query)
        )
    paginator = Paginator(tasks, 10)  # 10 مهام في كل صفحة
    page_number = request.GET.get('page')  # نقرأ رقم الصفحة من الرابط
    page_obj = paginator.get_page(page_number)  # لو الرقم غلط، بيرجع أقرب صفحة موجودة

    
    # ✅ تجهيز البيانات للفورم والفلاتر
    all_sites = Site.objects.all().values_list('id', 'name')
    all_writers = [(u.id, u.get_full_name() or u.username) for u in User.objects.filter(role='employee')]


    if request.user.role == 'manager':
        if request.method == 'POST':
            form = TaskForm(request.POST, user=request.user)
            if form.is_valid():
                task = form.save(commit=False)

                task.publish_date = get_valid_publish_date(task_type_wrab=task.article_type_W_R_A_B.type, 
                                                           site_name=task.publish_site.name,
                                                           writer=task.writer)

                task.created_by = request.user
                task.save()


                # ✅ إنشاء إشعار للموظف
                Notification.objects.create(
                    user=task.writer,
                    message=f"📌  تم اضافة  مهمة جديدة: وهي {task.article_type_W_R_A_B} لـ {task.article_title}",
                    link=f"/tasks/task/{task.id}/details/"
                )
                return redirect('task_list')
        else:
            form = TaskForm(user=request.user)

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'form': form,
        'notifications': notifications,
        'writers': all_writers, 
        'sites': all_sites,
        'selected_writer': writer_filter,
        'selected_status': status_filter,
        'selected_site': site_filter,
        'search_query': search_query,
        'page_obj': page_obj,
    })


#وظيفة  حذف المهمام
@role_required('manager')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    
    return redirect('task_list')

#وظيفة  تعديل المهمام
@role_required('manager')
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    form = TaskForm(request.POST or None, instance=task)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('task_list')
    tasks = Task.objects.all().order_by('-id')
    return render(request, 'tasks/task_list.html', {'form': form, 'tasks': tasks, 'edit_mode': True, 'task_id': task.id})

#وظيفة عرض المهمام للموظف
@login_required
def my_tasks(request):
    tasks = Task.objects.filter(writer=request.user).order_by('-publish_date')
    notifications = request.user.notifications.filter(is_read=False)

    # ⬇️ الفلاتر من الـ GET
    status_filter = request.GET.get('status')
    site_filter = request.GET.get('site')
    search_query = request.GET.get('q')

    # ⬇️ تطبيق الفلاتر
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if site_filter:
        tasks = tasks.filter(publish_site__id=site_filter)
    if search_query:
        tasks = tasks.filter(
             Q(article_title__icontains=search_query) |
             Q(article_details__icontains=search_query) |
             Q(article_type_W_R_A_B__type__icontains=search_query)
        )

    paginator = Paginator(tasks, 10)  # 10 مهام في كل صفحة
    page_number = request.GET.get('page')  # نقرأ رقم الصفحة من الرابط
    page_obj = paginator.get_page(page_number)  # لو الرقم غلط، بيرجع أقرب صفحة موجودة

    # ⬇️ قائمة المواقع للاستخدام في الفلتر
    sites = Site.objects.all().values_list('id', 'name')

    return render(request, 'tasks/my_tasks.html', {
        'tasks': page_obj,
        'notifications': notifications,
        'sites': sites,
        'selected_status': status_filter,
        'selected_site': site_filter,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
    })


#تعديل الحالة
User = get_user_model()
@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.user != task.writer and request.user.role != 'manager':
        return redirect('no_permission')
    
    new_status = request.POST.get('status')
    if new_status in ['in_progress', 'done', 'publish', 'upload']:
        task.status = new_status
        task.save()

        # إرسال إشعار للمدير
        managers = User.objects.filter(role='manager')
        for manager in managers:
            Notification.objects.create(
                user=manager,
                message=f"قام {request.user.get_full_name()} بتحديث حالة المهمة '{task.article_title}' إلى {get_status_label(new_status)}",
                link=f"/tasks/task/{task.id}/details/"
            )
    
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))

#تعديل اللينك 
@login_required
def update_article_link(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        article_link = request.POST.get('article_link')
        task.article_link = article_link
        task.save() 

    previous_page = request.META.get('HTTP_REFERER', reverse('my_tasks'))
    return redirect(previous_page)

#وظيفة عرض المهمة بشكل منفصل 


def task_details(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # السماح للمدير أو الكاتب أو المصمم بالوصول
    if request.user != task.writer and request.user.role not in ['manager', 'designer']:
        return redirect('no_permission')

    # تجهيز قوائم الاختيارات للتمبلت
    status_choices = Task._meta.get_field('status').choices
    image_type_choices = Task._meta.get_field('image_type').choices
    is_need_image = Task._meta.get_field('is_need_image').choices
    image_status= Task._meta.get_field('image_status').choices

    if request.method == 'POST':
        if request.user.role == 'manager':
            # المدير يستخدم الفورم الكامل
            form = TaskForm(request.POST, instance=task, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('task_details', task_id=task.id)

        elif request.user.role == 'designer':
            # المصمم يحدّث الحقول المسموح بها فقط
            allowed_fields = ['image_type', 'image_details', 'is_need_image','image_status']
            for field in allowed_fields:
                value = request.POST.get(field)
                if value is not None:
                    setattr(task, field, value)
            task.save()
            return redirect('task_details', task_id=task.id)

        else:
            # الموظف العادي يحدّث الحقول المسموح بها فقط
            allowed_fields = ['status', 'article_link', 'image', 'image_type', 'image_details', 'is_need_image','image_status']
            for field in allowed_fields:
                value = request.POST.get(field)
                if value is not None:
                    setattr(task, field, value)
            task.save()
            return redirect('task_details', task_id=task.id)

    else:
        if request.user.role == 'manager':
            form = TaskForm(instance=task, user=request.user)
        else:
            form = None  # المصمم والموظف العادي يستخدمون الحقول مباشرة في التمبلت

    return render(request, 'tasks/task_details.html', {
        'form': form,
        'task': task,
        'status_choices': status_choices,
        'image_type_choices': image_type_choices,
        'IS_NEED_IMAGE': is_need_image,
        'image_status': image_status,
    })

#وظيفة تحويل الصور للمصميم
@role_required('manager','designer')
def image_to_Designer(request):
    search_query = request.GET.get("q", "")
    selected_writer = request.GET.get("writer", "")
    selected_status = request.GET.get("image_status", "")
    selected_site = request.GET.get("site", "")

    tasks = Task.objects.filter(is_need_image="YES")

    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(writer__username__icontains=search_query) |
            Q(writer__first_name__icontains=search_query) |
            Q(writer__last_name__icontains=search_query)
        )

    if selected_writer:
        tasks = tasks.filter(writer_id=selected_writer)

    if selected_status:
        tasks = tasks.filter(image_status=selected_status)

    if selected_site:
        tasks = tasks.filter(publish_site_id=selected_site)
    
    # الباجيناشن
    paginator = Paginator(tasks, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    writer_ids = Task.objects.values_list("writer_id", flat=True).distinct()
    writers = [(w.id, w.get_full_name() or w.username) for w in User.objects.filter(id__in=writer_ids)]
    sites = Task.objects.values_list("publish_site__id", "publish_site__name").distinct()
    image_status = [
        ('in_progress', '⏳ جاري العمل'),
        ('send', 'تم الارسال للكاتب'),
        ('publish', '✅ تم الرفع على الموقع'),
    ]

    context = {
        "tasks": page_obj,
        "page_obj": page_obj,
        "search_query": search_query,
        "writers": writers,
        "selected_writer": selected_writer,
        "selected_status": selected_status,
        "sites": sites,
        "selected_site": selected_site,
        "image_status": image_status,
    }

    return render(request, "tasks/image_form.html", context)


@role_required('manager','designer', 'employee')
def update_image_status(request, task_id):
    task= get_object_or_404 (Task ,id=task_id)
    new_status = request.POST.get("image_status")

    # تحقق أن القيمة الجديدة موجودة في الخيارات
    valid_statuses = ['in_progress', 'send', 'publish']
    if new_status in valid_statuses:
        task.image_status = new_status
        task.save()
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))

#وظيفة البحث عن الرابط المنشور من خلال صفحة 
def auto_update_tasks(keyword=None):
    tasks = Task.objects.filter(status="done")
    print(f"عدد المهام قبل التحديث: {tasks.count()}")


    for task in tasks:
        # لو فيه كلمة محددة، نتأكد إنها موجودة في عنوان المقال
        if keyword and keyword not in task.article_title:
            continue  # نتجاوز المهمة لو الكلمة مش موجودة

        result = check_if_task_published(task.article_title)

        if result["found"]:
            task.status = "published"
            task.published_url = result["url"]
            task.save()
            print(f"[✔] Task {task.id} published at {result['url']} (score {result['score']})")
        else:
            print(f"[✘] Task {task.id} NOT found (score {result['score']})")
        

def update_task_published_url(task_id, single_url=None):
    """
    لو اتبعت single_url، هيتعامل مع رابط واحد فقط بدل البحث في sitemap.
    """
    task = get_object_or_404(Task, id=task_id)
    
    if single_url:
        # إضافة الرابط اللي جاي من المستخدم مباشرة
        task.published_url = single_url
        task.status = 'published'
        task.save()
        return True, [(single_url, None, 0)]  # نفس شكل القائمة القديمة
    else:
        if not task.publish_site or not task.publish_site.sitemaps_links:
            return False, None

        sitemap_urls = task.publish_site.sitemaps_links.strip().splitlines()
        keyword = task.article_title

        all_found_links = []

        for sitemap_url in sitemap_urls:
            found_links = url_form_sitemap_html(sitemap_url, keyword)
            all_found_links.extend(found_links)

        if all_found_links:
            # إزالة التكرارات
            seen = set()
            unique_links = []
            for link, anchor_text, match_count in all_found_links:
                if link not in seen:
                    unique_links.append((link, anchor_text, match_count))
                    seen.add(link)

            task.published_url = ','.join([link[0] for link in unique_links])
            task.status = 'published'
            task.save()
            return True, unique_links
        else:
            return False, None
