from django.urls import path 
from .views import UserRegistraionView, UserLoginView, UserBankAccountUpdateView
from . import views
urlpatterns = [
      
    path('register/', UserRegistraionView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', UserBankAccountUpdateView.as_view(), name='profile' ),
    
]
