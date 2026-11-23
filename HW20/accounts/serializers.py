import re

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class RegisterSerializer(serializers.ModelSerializer):
    """Регистрация: обязательные поля, формат email, уникальность логина и email,
    сложность пароля. Пароль хэшируется в create_user()."""

    username = serializers.CharField(
        min_length=3,
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                lookup="iexact",
                message="Пользователь с таким логином уже существует.",
            )
        ],
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                lookup="iexact",
                message="Пользователь с таким email уже существует.",
            )
        ],
    )
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2")
        read_only_fields = ("id",)

    def validate_password(self, value):
        """Минимальные требования к сложности пароля."""
        errors = []
        if len(value) < 8:
            errors.append("Пароль должен содержать не менее 8 символов.")
        if not re.search(r"[A-Z]", value):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву.")
        if not re.search(r"[a-z]", value):
            errors.append("Пароль должен содержать хотя бы одну строчную букву.")
        if not re.search(r"\d", value):
            errors.append("Пароль должен содержать хотя бы одну цифру.")
        if errors:
            raise serializers.ValidationError(errors)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": ["Пароли не совпадают."]})
        # Стандартные валидаторы Django (похожесть на логин, частые пароли и т.д.)
        candidate = User(username=attrs["username"], email=attrs["email"])
        try:
            validate_password(attrs["password"], candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        # create_user хэширует пароль (в БД хранится не сам пароль, а его хэш)
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError(
                "Неверный логин или пароль.", code="authorization"
            )
        attrs["user"] = user
        return attrs
