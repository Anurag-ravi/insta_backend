from django.urls import path
from users import views
urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('verify_account/<str:hash>', views.verify_account),
]