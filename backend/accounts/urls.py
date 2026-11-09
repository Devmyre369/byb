


from django.urls import path

from .api_views import (
    RegisterAPIView,
    send_otp,
    verify_otp,
    login,
    logout,
    current_user,
    BYBTokenRefreshView,
    public_user_profile,
    upload_profile_picture,
)

app_name = "accounts"

urlpatterns = [
    # Registration and email verification
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("send-otp/", send_otp, name="send-otp"),
    path("verify-otp/", verify_otp, name="verify-otp"),

    # Authentication
    path("login/", login, name="login"),
    path("token/refresh/", BYBTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", logout, name="logout"),

    # Own profile
    path("me/", current_user, name="current-user"),
    path(
        "me/profile-picture/",
        upload_profile_picture,
        name="upload-profile-picture",
    ),

    # Public profiles
    path("users/<str:username>/", public_user_profile, name="public-profile"),
]
