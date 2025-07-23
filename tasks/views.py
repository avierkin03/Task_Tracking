from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from tasks import models
from tasks.forms import TaskForm, TaskFilterForm, CommentForm
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from tasks.mixins import UserIsOwnerMixin
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages

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
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = models.Task
    context_object_name = "task"
    template_name = "tasks/task_detail.html"

    # перевизнаємо метод, який буде передавати додаткову форму для додавання коментарів до контексту шаблону
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()  # Додаємо порожню форму коментаря в контекст
        return context

    # перевизнаємо метод для опрацювання post запитів, для додаткового опрацювання запиту на створення коментаря через форму
    def post(self, request, *args, **kwargs):
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.task = self.get_object()
            comment.save()
            return redirect('tasks:task-detail', pk=comment.task.pk)
        else:
            # Тут можна обробити випадок з невалідною формою
            pass


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


# В'ю для оновлення коментаря
class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Comment
    fields = ['content']
    template_name = 'tasks/edit_comment.html'

    # перевизначимо метод form_valid
    def form_valid(self, form):
        comment = self.get_object()
        if comment.author != self.request.user:
            raise PermissionDenied("Ви не можете редагувати цей коментар.")
        return super().form_valid(form)
    
    # перевизначимо метод, що вказує URL, на який користувач буде перенаправлений після успішного оновлення коментаря через форму
    def get_success_url(self):
        return reverse_lazy('tasks:task-detail', kwargs={'pk': self.object.task.pk})


# В'ю для видалення коментаря
class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Comment
    template_name = 'tasks/delete_comment.html'

    def dispatch(self, request, *args, **kwargs):
        # Отримуємо об'єкт коментаря
        comment = self.get_object()
        # Перевіряємо, чи є користувач автором коментаря
        if comment.author != self.request.user:
            # Додаємо повідомлення
            messages.error(self.request, "Ви не можете видаляти коментарі інших користувачів.")
            # Перенаправляємо назад на сторінку задачі
            return HttpResponseRedirect(reverse_lazy('tasks:task-detail', kwargs={'pk': comment.task.pk}))
        return super().dispatch(request, *args, **kwargs)

    # # перевизнаємо метод, який повертає моделі коментарів (повертаємо лише коментарі того юзера, котрий відправив запит)
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(author=self.request.user)

    # перевизначимо метод, що вказує URL, на який користувач буде перенаправлений після успішного видалення коментаря
    def get_success_url(self):
        return reverse_lazy('tasks:task-detail', kwargs={'pk': self.object.task.pk})


# В'ю для додавання\видалення лайка з коментаря
class CommentLikeToggle(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(models.Comment, pk=self.kwargs.get('pk'))
        # дивимось чи існують лайки для цього коментаря від цього юзера
        like_qs = models.Like.objects.filter(comment=comment, user=request.user)
        if like_qs.exists():
            like_qs.delete()
        else:
            models.Like.objects.create(comment=comment, user=request.user)
        return HttpResponseRedirect(comment.get_absolute_url())
    

# В'ю для логіну користувача
class CustomLoginView(LoginView):
    template_name = "tasks/login.html"
    # після успішного логіну перенаправляємо юзера на сторінку, посилання на яку вказано в settings
    redirect_authenticated_user = True


# В'ю для логауту користувача
class CustomLogoutView(LogoutView):
    next_page = "tasks:login"


# В'ю для реєстрації користувача
class RegisterView(CreateView):
    template_name = "tasks/register.html"
    form_class = UserCreationForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(reverse_lazy("tasks:login"))