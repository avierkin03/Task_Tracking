from django.urls import path
from tasks import views

urlpatterns = [
    path('', views.TaskListView.as_view(), name="task-list"),
    path('<int:pk>/', views.TaskDetailView.as_view(), name="task-detail"),
    path('task-create', views.TaskCreateView.as_view(), name="task-create"),
    path('<int:pk>/status/', views.TaskChangeStatusView.as_view(), name="task-status"),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(), name="task-update"),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name="task-delete"),
    path('comment/edit/<int:pk>/', views.CommentUpdateView.as_view(), name='edit_comment'),
    path('comment/delete/<int:pk>/', views.CommentDeleteView.as_view(), name='delete_comment'),
    path('comment/like/<int:pk>/', views.CommentLikeToggle.as_view(), name='comment-like-toggle'),
    path('login/', views.CustomLoginView.as_view(), name="login"),
    path('logout/', views.CustomLogoutView.as_view(), name="logout"),
    path('register/', views.RegisterView.as_view(), name="register"),
]

app_name = "tasks"