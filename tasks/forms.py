from django import forms
from .models import Task
from accounts.models import Users
from ckeditor.widgets import CKEditorWidget  # استدعاء CKEditor

class TaskForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())  # استخدام CKEditor للحقل content

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user

        if user and user.role != 'manager':
            # الموظف العادي يعدل فقط الحقول المسموح بها
            allowed_fields = ['image', 'image_type', 'image_details', 'article_link', 'status', 'content', 'original_article_url']
            for field in list(self.fields.keys()):
                if field not in allowed_fields:
                    self.fields[field].widget = forms.HiddenInput()
                    self.fields[field].required = False

            # Writer مخفي
            self.fields['writer'].widget = forms.HiddenInput()
            self.fields['writer'].required = False

            # تاريخ النشر مخفي
            self.fields['publish_date'].widget = forms.HiddenInput()
            self.fields['publish_date'].required = False

        else:
            # المدير يشوف كل الحقول ويقدر يعدل publish_date
            self.fields['writer'].queryset = Users.objects.filter(role='employee')
            self.fields['publish_date'].widget = forms.DateInput(attrs={'type': 'date'})

    class Meta:
        model = Task
        fields = '__all__'

    def save(self, commit=True):
        task = super().save(commit=False)

        if self.user and self.user.role != 'manager':
            # اجبر الكاتب يبقى المستخدم الحالي
            task.writer = self.user
            # الموظف العادي → احتفظ بتاريخ النشر الموجود
            if self.instance and self.instance.pk:
                task.publish_date = self.instance.publish_date

        if commit:
            task.save()
        return task
