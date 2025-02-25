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
from .response_utils import (
    success_response,
    error_response,
    not_found_response,
    bad_request_response,
    unauthorized_response,
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
            return Response(
                success_response(
                    success_response(
                        post_serializer.data, message="post created successfully"
                    )
                ),
                status=status.HTTP_201_CREATED,
            )

        # If the data is not valid, return an error response with the serializer's errors and a 400 Bad Request status code

        return Response(
            error_response(error_response(post_serializer.error_messages)),
            status=status.HTTP_400_BAD_REQUEST,
        )


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
            return Response(
                success_response(serializer.data), status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetPostWithCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            # Retrieve all posts and prefetch related comments
            posts = Post.objects.prefetch_related("comments").all()

            # Prepare the response data
            response_data = []

            for post in posts:
                # Serialize the post
                post_serializer = PostSerializer(post)

                # Serialize the comments
                comments_serializer = CommentSerializer(post.comments.all(), many=True)

                filtered_comments = [
                    {
                        "content": comment["content"],
                        "post": comment["post"],
                        "user": comment["user"],
                    }
                    for comment in comments_serializer.data
                ]

                # Append post and its comments to the response data
                response_data.append(
                    {"post": post_serializer.data, "comments": filtered_comments}
                )

            return Response(
                success_response(
                    response_data, message="Posts and comments  retrieved successfully"
                ),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                error_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return None

    def patch(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response(
                not_found_response("Post not found"), status=status.HTTP_404_NOT_FOUND
            )

        if post.author != request.user:
            return Response(
                unauthorized_response("You are not authorized to perform this action"),
                status=status.HTTP_403_FORBIDDEN,
            )

        post_serializer = PostSerializer(
            post, data=request.data, context={"request": request}, partial=True
        )

        if post_serializer.is_valid():
            post_serializer.save()

            return Response(
                success_response(post_serializer.data, message="Post Updated"),
                status=status.HTTP_200_OK,
            )

        return Response(
            bad_request_response(post_serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class DeletePostView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                not_found_response("Post not found"), status=status.HTTP_404_NOT_FOUND
            )

        if post.author != request.user:
            return Response(
                unauthorized_response("You are not authorized to perform this action"),
                status=status.HTTP_403_FORBIDDEN,
            )
        post.delete()
        return Response(
            success_response(data=None, message="Post deleted successfully"),
            status=status.HTTP_204_NO_CONTENT,
        )


class DeleteCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response(
                not_found_response("Comment not found"),
                status=status.HTTP_404_NOT_FOUND,
            )

        if comment.user != request.user:
            return Response(
                unauthorized_response("You are not authorized to perform this action"),
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.delete()
        return Response(
            success_response(data=None, message="Comment deleted successfully"),
            status=status.HTTP_204_NO_CONTENT,
        )
