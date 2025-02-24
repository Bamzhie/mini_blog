# myapp/views.py
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Post, Comment
from .serializers import CustomUserSerializer, PostSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch


class RegisterView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.password = make_password(user.password)
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = CustomUser.objects.filter(email=email).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)

            # Explicitly add user_id to the token
            refresh["user_id"] = str(user.user_id)  # Convert UUID to string

            return Response(
                {
                    "message": "Login successful",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Initialize the serializer with the incoming request data and context
        post_serializer = PostSerializer(
            data=request.data, context={"request": request}
        )

        # Check if the data is valid according to the serializer's validation rules
        if post_serializer.is_valid():
            # Save the post instance with the current user as the author
            post_serializer.save()

            # Return a success response with the serialized data and a 201 Created status code
            return Response(post_serializer.data, status=status.HTTP_201_CREATED)

        # If the data is not valid, return an error response with the serializer's errors and a 400 Bad Request status code
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentOnPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = CommentSerializer(
            data=request.data,
            context={"request": request, "post": post},  # ✅ Pass request in context
        )

        if serializer.is_valid():
            serializer.save()  # ✅ Now 'request' and 'post' are available in create()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetPostWithCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve all posts and prefetch related comments
        posts = Post.objects.prefetch_related("comments").all()

        # Prepare the response data
        response_data = []

        for post in posts:
            # Serialize the post
            post_serializer = PostSerializer(post)

            # Serialize the comments
            comments_serializer = CommentSerializer(post.comments.all(), many=True)

            # Append post and its comments to the response data
            response_data.append(
                {"post": post_serializer.data, "comments": comments_serializer.data}
            )

        return Response(response_data)
