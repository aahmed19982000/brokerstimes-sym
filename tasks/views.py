from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import login_required 
from accounts.decorators import role_required
from accounts.models import Notification
from django.contrib.auth import get_user_model
from .utils import get_valid_publish_date 
from django.utils import timezone
from django.contrib import messages
from categories.models import Site
def get_status_label(code):
    return {
        'in_progress': '⏳ جاري العمل',
        'upload': '📤 تم الرفع',
        'publish': '📢 تم النشر',
        'done': '✅ مكتملة'
    }.get(code, code)

#وظيفة اناء المهمام وعرضها 
@role_required('manager')

def task_list(request):
    tasks = Task.objects.all().order_by('-publish_date')
    form = None

    notifications = Notification.objects.filter(user=request.user, is_deleted=False).order_by('-created_at')[:10]
     # ✅ الحصول على بيانات الفلترة من GET
    writer_filter = request.GET.get('writer')
    status_filter = request.GET.get('status')
    site_filter = request.GET.get('site')

    if writer_filter:
     tasks = tasks.filter(writer_id=writer_filter)

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if site_filter:
        tasks = tasks.filter(publish_site__id=site_filter)

    
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
        'selected_site': site_filter
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

    # ⬇️ تطبيق الفلاتر
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if site_filter:
        tasks = tasks.filter(publish_site__id=site_filter)

    # ⬇️ قائمة المواقع للاستخدام في الفلتر
    sites = Site.objects.all().values_list('id', 'name')

    return render(request, 'tasks/my_tasks.html', {
        'tasks': tasks,
        'notifications': notifications,
        'sites': sites,
        'selected_status': status_filter,
        'selected_site': site_filter,
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
                message=f"قام {request.user.username} بتحديث حالة المهمة '{task.article_title}' إلى {get_status_label(new_status)}",
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
        return redirect('my_tasks')  

    return redirect('my_tasks')

#وظيفة عرض المهمة بشكل منفصل 
def task_details(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'tasks/task_details.html', {'task': task})


