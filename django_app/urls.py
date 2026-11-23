from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("how-it-works/", views.how_it_works_view, name="how_it_works"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("terms/", views.terms_view, name="terms"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("upload/", views.upload_view, name="upload"),
    path("verify/", views.verify_view, name="verify"),
    path("certificate/<int:entry_id>/", views.certificate_download_view, name="certificate_download"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # API endpoints
    path("api/wallet-login/", views.api_wallet_login, name="api_wallet_login"),
    path("api/hash/", views.api_compute_hash, name="api_compute_hash"),
    path("api/record/", views.api_record_entry, name="api_record_entry"),
]
