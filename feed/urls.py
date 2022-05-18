from django.urls import path
from feed import views
urlpatterns = [
    path('post/new/', views.create_post),
    path('post/edit/<int:id>/', views.update_post),
    path('post/delete/<int:id>/', views.delete_post),
    path('feed/<int:index>/', views.get_feed),
]