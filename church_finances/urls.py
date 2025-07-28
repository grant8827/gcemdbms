from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.user_login_view, name="login"),
    path("logout/", views.user_logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("transactions/", views.transaction_list_view, name="transaction_list"),
    path("transactions/add/", views.transaction_create_view, name="transaction_create"),
    path(
        "transactions/<int:pk>/",
        views.transaction_detail_view,
        name="transaction_detail",
    ),
    path(
        "transactions/<int:pk>/edit/",
        views.transaction_update_view,
        name="transaction_update",
    ),
    path(
        "transactions/<int:pk>/delete/",
        views.transaction_delete_view,
        name="transaction_delete",
    ),
    
    # Member Management URLs
    path("members/", views.member_list_view, name="member_list"),
    path("members/add/", views.member_create_view, name="member_create"),
    path("members/<int:pk>/", views.member_detail_view, name="member_detail"),
    path("members/<int:pk>/edit/", views.member_update_view, name="member_update"),
    
    # Tithing Management URLs
    path("tithes/", views.tithing_list_view, name="tithing_list"),
    path("tithes/add/", views.tithing_create_view, name="tithing_create"),
    path("tithes/<int:pk>/edit/", views.tithing_update_view, name="tithing_update"),
    path("tithes/<int:pk>/delete/", views.tithing_delete_view, name="tithing_delete"),
    
    # Printable Reports URLs
    path("members/<int:pk>/report/", views.member_tithing_report, name="member_tithing_report"),
    path("reports/annual-summary/", views.annual_tithing_summary, name="annual_tithing_summary"),
]
