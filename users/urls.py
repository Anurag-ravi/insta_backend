from django.urls import path
from users import views
urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('verify_account/<str:hash>', views.verify_account),
    path('reset_password/', views.reset_pass),
    path('forgot_password/<str:hash>', views.forgot_pass),

    path('check_username/', views.check_username),
    path('search/', views.get_search_result),
    path('update_profile/', views.update_profile),
    path('profile/', views.get_profile),
    
    path('follow/', views.follow),
    path('follow_suggestion/', views.follow_suggestion),
    path('get_followers/', views.get_followers),
]