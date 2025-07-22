from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Модель завдання
class Task(models.Model):
    STATUS_CHOISES = [
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("done", "Done")
    ]

    PRIORITY_CHOISES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High")
    ]

    title = models.CharField(max_length=256)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOISES, default="todo")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOISES, default="medium")
    due_date = models.DateField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('tasks:task-detail', kwargs={'pk': self.pk})
    

# Модель коментаря
class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    media = models.FileField(upload_to="comments_media/", blank=True, null=True)

    def get_absolute_url(self):
        return self.task.get_absolute_url()


# Модель лайка
class Like(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_comments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')  # Забезпечує унікальність лайків
    