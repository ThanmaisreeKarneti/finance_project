from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('', views.login_page, name='home'), 
    path('login/', views.login_page, name='login'),  # Redirects the root URL to the login page
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('wallet/', views.wallet, name='wallet'),
    path('add-income/', views.add_income, name='add_income'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('add-category/', views.add_category, name='add_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('edit-balance/', views.edit_balance, name='edit_balance'),
    path('settings/', views.settings_view, name='settings'),
    path('notifications/', views.notifications, name='notifications'),
    path('overview/', views.overview, name='overview'),
    path('activities/', views.recent_activities, name='activities'),
    path('profit-loss/', views.profit_loss, name='profit_loss'),
]
    
