from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from tasks import models
from tasks.forms import TaskForm, TaskFilterForm
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from tasks.mixins import UserIsOwnerMixin
from django.http import HttpResponseRedirect

# Список існуючих задач
class TaskListView(ListView):
    model = models.Task
    context_object_name = "tasks"
    template_name = "tasks/task_list.html"

    # перевизнаємо метод, який повертає моделі тасків (додаємо врахування обраних фільтрів)
    def get_queryset(self):
        # отримаємо queryset, який видає дефолтна функція
        queryset = super().get_queryset()
        # отрмуємо статус від користувача
        status = self.request.GET.get("status", "")
        # отрмуємо пріоритет від користувача
        priority = self.request.GET.get("priority", "")
        # перевірка обраних фільтрів
        if status:
            queryset = queryset.filter(status = status)
        if priority:
            queryset = queryset.filter(priority = priority)
        return queryset
    
    # перевизнаємо метод, який буде передавати додаткову форму фільтрації до контексту шаблону
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = TaskFilterForm(self.request.GET) # передаємо все тіло запиту у форму
        return context


# Детальний перегляд задачі
# DetailView приймає primary key
class TaskDetailView(DetailView):
    model = models.Task
    context_object_name = "task"
    template_name = "tasks/task_detail.html"


# Створення нової задачі
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = models.Task
    template_name = "tasks/task_form.html"
    form_class = TaskForm
    # куди перенаправити користувача, після створення задачі
    success_url = reverse_lazy("tasks:task-list")

    # перевизначимо метод form_valid
    def form_valid(self, form):
        form.instance.creator = self.request.user
        # запускаємо цей перевизначений метод із батьківського класу
        return super().form_valid(form)


# В'ю для зміни статуса завдання
class TaskChangeStatusView(LoginRequiredMixin, UserIsOwnerMixin, View):
    # для опрацьовування даних в кастомних View треба перевизначити один із методів, які ми будемо використовувати
    def post(self, request, *args, **kwargs):
        # отримуємо об'єкт задачі
        task = self.get_object()

        # Отримуємо значення статусу з POST-запиту
        new_status = self.request.POST.get("task_status")

        # Перевіряємо, чи отримане значення є допустимим
        valid_statuses = ["todo", "in_progress", "done"]
        if new_status in valid_statuses:
            task.status = new_status
            task.save()
            
        return HttpResponseRedirect(reverse_lazy("tasks:task-list"))
    
    def get_object(self):
        task_id = self.kwargs.get("pk")
        return get_object_or_404(models.Task, pk = task_id)


# В'ю для оновлення таски
class TaskUpdateView(LoginRequiredMixin, UserIsOwnerMixin, UpdateView):
    model = models.Task
    form_class = TaskForm
    template_name = "tasks/task_update_form.html"
    # перенаправляємо користувача на список задач, після того як він оновив таску
    success_url = reverse_lazy("tasks:task-list")


# В'ю для видалення таски
class TaskDeleteView(LoginRequiredMixin, UserIsOwnerMixin, DeleteView):
    model = models.Task
    template_name = "tasks/task_delete_confirmation.html"
    # перенаправляємо користувача на список задач, після того як він оновив таску
    success_url = reverse_lazy("tasks:task-list")