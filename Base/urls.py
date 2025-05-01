from django.urls import path
from . import views

urlpatterns=[
    path('login/',views.loginPage,name="login"),
    path('signup/',views.signupPage,name="signup"),
    path('logout/',views.logoutPage,name="logout"),
    path('',views.home,name="Home"),
    path('delete-comment/<int:msg_id>/<int:room_id>',views.delete_comment,name="delete-comment"),
    path('edit-comment/<int:msg_id>/<int:room_id>',views.edit_comment,name="edit-comment"),
    path('room/<int:room_id>/',views.room,name='Room'),
    path('create-room/',views.create_room,name="create-room"),
    path('update-room/<int:room_id>/',views.update_room,name="update-room"),
    path('delete-room/<int:room_id>/',views.delete_room,name="delete-room"),
    path('delete-activity/<int:msg_id>/',views.delete_activity,name="delete-activity"),
    path('user-profile/<int:id>/',views.userProfile,name="user-profile"),
    path('update-user/',views.updateUser,name="update-user"),
    path('topics/',views.topics,name="topics"),
    path('activity/',views.activity,name="activity"),
    
]

