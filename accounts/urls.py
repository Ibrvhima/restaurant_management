from django.urls import path
from . import views
from . import views_init

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('init-db/', views_init.init_database, name='init_database'),
    
    # URLs admin (préfixe 'system' pour éviter conflit avec /admin/)
    path('system/users/', views.admin_user_list, name='admin_user_list'),
    path('system/users/create/', views.admin_create_user, name='admin_create_user'),
    path('system/users/<int:user_id>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),
    path('system/data/', views.admin_data_management, name='admin_data_management'),
    path('system/data/clear/commandes/', views.admin_clear_commandes, name='admin_clear_commandes'),
    path('system/data/clear/paiements/', views.admin_clear_paiements, name='admin_clear_paiements'),
    path('system/data/clear/depenses/', views.admin_clear_depenses, name='admin_clear_depenses'),
    path('system/data/reset/caisse/', views.admin_reset_caisse, name='admin_reset_caisse'),
    path('system/export/excel/', views.export_excel_dashboard, name='export_excel_dashboard'),
    path('system/export/pdf/', views.export_pdf_dashboard, name='export_pdf_dashboard'),
]
