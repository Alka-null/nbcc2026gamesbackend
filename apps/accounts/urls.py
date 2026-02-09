from django.urls import path

from .views import CodeLoginView, ProfileView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('code-login/', CodeLoginView.as_view(), name='code-login'),
    path('me/', ProfileView.as_view(), name='profile'),
]
