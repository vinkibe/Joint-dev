from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),

    path('', views.home, name='home'),
    path('room/<str:id>/', views.room, name='room'),
    path('profile/<str:id>/', views.userProfile, name='user-profile'),
    path('code-editor/', views.code_editor, name='code-editor'),
    path('save/', views.save_code, name='save_code'), 
    path('join-meet/', views.joinMeeting, name='join-meet'),
    path('google_meet/', views.google_meet_view, name='google_meet_view'),
    path('auth/google_meet/', views.google_meet_auth, name='google_meet_auth'),
    path('auth/google_meet/callback/', views.google_meet_callback, name='google_meet_callback'),
    

    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<str:id>/', views.updateRoom, name='update-room'),
    path('delete-room/<str:id>/', views.deleteRoom, name='delete-room'),
    path('delete-message/<str:id>/', views.deleteMessage, name='delete-message'),

    path('update-user/', views.updateUser, name='update-user'),

    path('topics/', views.topicsPage, name='topics'),
    path('activity/', views.activityPage, name='activity'),

    path('repo/', views.repo, name='repo'),
    path('add_document/', views.add_document, name='add_document'),
    path('delete_document/<int:document_id>/', views.delete_document, name='delete_document'),
]