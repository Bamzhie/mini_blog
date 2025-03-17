from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import CustomUserSerializer
from .response_utils import (
    success_response,
)


class RegisterView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            password = make_password(serializer.validated_data["password"])
            user = serializer.save(password=password)

            return Response(
                success_response(
                    serializer.data, message="Welcome! account created successfully"
                ),
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = CustomUser.objects.filter(email=email).first()

        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        print(f"User found: {user.email}")

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)

            # Explicitly add user_id to the token
            refresh["user_id"] = str(user.user_id)  # Convert UUID to string
            data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response(
                success_response(data, message="Login successful"),
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
