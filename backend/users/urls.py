from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("verify-email/<str:token>/", views.verify_email, name="verify_email"),
    path("resend-verification/", views.resend_verification, name="resend_verification"),
    path("request-magic-link/", views.request_magic_link, name="request_magic_link"),
    path("login/", views.login_with_magic_link, name="login_magic_link"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.logout, name="logout"),
    path("me/", views.current_user, name="current_user"),
    path("me/delete/", views.delete_account, name="delete_account"),
]
