from django.urls import path
from feed import views
urlpatterns = [
    path('post/new/', views.create_post),
    path('post/edit/<int:id>/', views.update_post),
    path('post/delete/<int:id>/', views.delete_post),
    path('post/like/<int:index>/', views.like_post),
    path('post/save/<int:index>/', views.save_post),
    path('post/<int:index>/', views.detailed_post),

    path('comment/new/', views.create_comment),
    path('comment/like/<int:index>/', views.like_comment),
    path('comment/edit/<int:index>/', views.update_comment),
    path('comment/delete/<int:index>/', views.delete_comment),

    
    path('feed/<int:index>/', views.get_feed),
]