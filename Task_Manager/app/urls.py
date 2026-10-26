from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app import views


router = DefaultRouter()
router.register("register", views.RegisterView, basename="register")
router.register("login", views.LoginView, basename="login")
router.register("tasks", views.TaskView, basename="tasks")

urlpatterns = [
    path("", include(router.urls))
]

