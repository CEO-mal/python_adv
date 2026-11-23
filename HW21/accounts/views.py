from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .authentication import revoke_access_token
from .serializers import LoginSerializer, RegisterSerializer


def _set_auth_cookies(response, access, refresh=None):
    """Токены кладём в httpOnly-cookie: JavaScript на странице их прочитать не может."""
    secure = not settings.DEBUG  # в разработке (http) cookie без Secure
    response.set_cookie(
        settings.AUTH_COOKIE_ACCESS,
        access,
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=secure,
        samesite="Lax",
        path="/",
    )
    if refresh is not None:
        response.set_cookie(
            settings.AUTH_COOKIE_REFRESH,
            refresh,
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            httponly=True,
            secure=secure,
            samesite="Lax",
            path="/api/auth/",  # refresh-cookie уходит только на адреса /api/auth/...
        )


def _delete_auth_cookies(response):
    response.delete_cookie(settings.AUTH_COOKIE_ACCESS, path="/")
    response.delete_cookie(settings.AUTH_COOKIE_REFRESH, path="/api/auth/")


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ - регистрация пользователя."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class LoginView(APIView):
    """POST /api/auth/login/ - вход: возвращает access и refresh, пишет их в httpOnly-cookie."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            non_field = serializer.errors.get("non_field_errors")
            code = status.HTTP_401_UNAUTHORIZED if non_field else status.HTTP_400_BAD_REQUEST
            return Response(serializer.errors, status=code)

        refresh = RefreshToken.for_user(serializer.validated_data["user"])
        access = str(refresh.access_token)
        response = Response({"access": access, "refresh": str(refresh)})
        _set_auth_cookies(response, access, str(refresh))
        return response


class RefreshView(APIView):
    """POST /api/auth/refresh/ - новый access по refresh (из cookie или из тела запроса).
    Старый refresh после обновления аннулируется (ротация + чёрный список)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        raw_refresh = request.data.get("refresh") or request.COOKIES.get(
            settings.AUTH_COOKIE_REFRESH
        )
        if not raw_refresh:
            return Response(
                {"detail": "Refresh-токен не передан."}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = TokenRefreshSerializer(data={"refresh": raw_refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response(
                {"detail": "Refresh-токен недействителен или аннулирован."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        data = serializer.validated_data
        response = Response(data)
        _set_auth_cookies(response, data["access"], data.get("refresh"))
        return response


class LogoutView(APIView):
    """POST /api/auth/logout/ - выход: refresh и access попадают в чёрный список,
    cookie с токенами удаляются."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        raw_refresh = request.data.get("refresh") or request.COOKIES.get(
            settings.AUTH_COOKIE_REFRESH
        )
        raw_access = request.COOKIES.get(settings.AUTH_COOKIE_ACCESS)
        if not raw_access:
            header = request.META.get("HTTP_AUTHORIZATION", "")
            if header.startswith("Bearer "):
                raw_access = header.split(" ", 1)[1]

        if not raw_refresh:
            return Response(
                {"detail": "Refresh-токен не передан."}, status=status.HTTP_400_BAD_REQUEST
            )

        # 1. refresh -> чёрный список (таблица BlacklistedToken)
        try:
            RefreshToken(raw_refresh).blacklist()
        except TokenError:
            pass  # уже недействителен - выходим в любом случае

        # 2. access -> чёрный список до конца срока жизни
        if raw_access:
            try:
                revoke_access_token(AccessToken(raw_access))
            except TokenError:
                pass

        response = Response({"detail": "Вы вышли из аккаунта."}, status=status.HTTP_200_OK)
        _delete_auth_cookies(response)  # 3. cookie удаляются
        return response
