from django import forms
from tasks.models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "priority", "due_date"]

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})
        self.fields["due_date"].widget.attrs["class"] += " my-custom=datepicker"


# Форма для налаштування фільтрів для тасків
class TaskFilterForm(forms.Form):
    STATUS_CHOISES = [
        ("", "Всі"),
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("done", "Done")
    ]
    PRIORITY_CHOISES = [
        ("", "Всі"),
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High")
    ]

    status = forms.ChoiceField(choices=STATUS_CHOISES, required=False, label="Статус")
    priority = forms.ChoiceField(choices=PRIORITY_CHOISES, required=False, label="Пріоритет")

    def __init__(self, *args, **kwargs):
        super(TaskFilterForm, self).__init__(*args, **kwargs)
        self.fields["status"].widget.attrs.update({"class": "form-control"})
        self.fields["priority"].widget.attrs.update({"class": "form-control"})