from django.urls import path
from . import views

urlpatterns = [
    ## Register & Login
    path('', views.index),
    path('register', views.register),
    path('login', views.login),
    path('recipe/', views.recipe),
    path('logout', views.logout),

    ## FUTURE ROUTES BERLOW
    path('save', views.save),
    path('recipes_saved', views.recipes_saved),
    path('delete/<int:card_id>', views.delete)
]