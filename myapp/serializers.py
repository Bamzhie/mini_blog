# myapp/serializers.py
from rest_framework import serializers
from .models import CustomUser, Post, Comment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from pprint import pprint


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "content", "created_at", "updated_at", "author")
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "author",
        )  # Author should be read-only

    def create(self, validated_data):
        # Assign the currently authenticated user as the author
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "created_at",
            "updated_at",
            "post",
            "user",
        )  # Include all necessary fields
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "post",
            "user",
        )  # Make `post` and `user` read-only

    def create(self, validated_data):

        request = self.context["request"]
        post = self.context["post"]

        # Set the user from the request and post from the context
        validated_data["user"] = request.user
        validated_data["post"] = post
        return super().create(validated_data)


class TokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Ensure user_id is included in the token
        token["user_id"] = str(user.user_id)  # Convert UUID to string

        return token
