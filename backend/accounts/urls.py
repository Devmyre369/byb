'''
from django.urls import path
from .api_views import RegisterAPIView

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
]


from django.urls import path

from .api_views import RegisterAPIView, send_otp

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("send-otp/", send_otp, name="send-otp"),
]


from django.urls import path

from .api_views import RegisterAPIView, send_otp, verify_otp

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("send-otp/", send_otp, name="send-otp"),
    path("verify-otp/", verify_otp, name="verify-otp"),
]
'''

from django.urls import path

from .api_views import (
    RegisterAPIView,
    send_otp,
    verify_otp,
    login,
    logout,
    current_user,
    BYBTokenRefreshView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("send-otp/", send_otp, name="send-otp"),
    path("verify-otp/", verify_otp, name="verify-otp"),

    path("login/", login, name="login"),
    path("token/refresh/", BYBTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", logout, name="logout"),
    path("me/", current_user, name="current-user"),
]