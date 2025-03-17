# myapp/serializers.py
from rest_framework import serializers
from .models import CustomUser, Post, Comment, PostImage
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from pprint import pprint
import cloudinary.uploader
import cloudinary


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("id", "image", "uploaded_at")


class PostSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:

        model = Post
        fields = (
            "id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "author",
            "images",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "author",
        )  # Author should be read-only

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        post = Post.objects.create(**validated_data)
        for image in images:
            result = cloudinary.uploader.upload(image, public_id=post.id)
            PostImage.objects.create(post=post, image=result["secure_url"])
        return post

    def get_images(self, obj):
        images = obj.images.all()
        return [PostImageSerializer(image).data for image in images]


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
