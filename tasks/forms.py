from django import forms
from .models import Task
from accounts.models import Users  

class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # نستقبل المستخدم من الـ view
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['publish_date'].required = False

        self.user = user

        # لو المستخدم مش مدير → نخفي حقل writer
        if user and user.role != 'manager':
            self.fields['writer'].widget = forms.HiddenInput()
            self.fields['writer'].required = False  # علشان ميظهرش خطأ

        # ممكن كمان نفلتر الكتاب مثلًا (اختياري)
        if user and user.role == 'manager':
            self.fields['writer'].queryset = Users.objects.filter(role='employee')

    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'publish_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        task = super().save(commit=False)
        # لو المستخدم مش مدير → عيّن الكاتب بنفسه
        if self.user and self.user.role != 'manager':
            task.writer = self.user
        if commit:
            task.save()
        return task
