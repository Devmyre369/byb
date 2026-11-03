from django.urls import path
from .api_views import RegisterAPIView

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
]