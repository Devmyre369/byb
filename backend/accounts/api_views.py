from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer


@api_view(["GET"])
def health_check(request):
    return Response({
        "status": "success",
        "message": "BYB backend is running!",
        "application": "Beyond Your Bubble",
    })


class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "status": "success",
            "message": "Registration successful. Please verify your email.",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "is_verified": user.is_verified,
            }
        }, status=status.HTTP_201_CREATED)