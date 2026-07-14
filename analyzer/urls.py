from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("history/", views.history, name="history"),
    # path("download-pdf/", views.download_pdf, name="download_pdf"),
    path(
        "download-pdf/<int:resume_id>/",
        views.download_pdf,
        name="download_pdf",
    ),
    path(
        "resume/<int:resume_id>/",
        views.resume_detail,
        name="resume_detail",
    ),
    path(
        "delete-resume/<int:resume_id>/",
        views.delete_resume,
        name="delete_resume",
    ),
    path("profile/", views.profile, name="profile"),
    path(
        "delete-resume/<int:resume_id>/",
        views.delete_resume,
        name="delete_resume",
    ),
    path(
        "resume/<int:resume_id>/",
        views.resume_detail,
        name="resume_detail",
    ),
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard",
    ),
    path(
        "export-csv/",
        views.export_csv,
        name="export_csv",
    ),
]
