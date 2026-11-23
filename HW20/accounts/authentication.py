from django.conf import settings
from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

REVOKED_PREFIX = "revoked_access:"


def revoke_access_token(validated_token):
    """Заносит access-токен в чёрный список до конца срока его жизни."""
    import time

    ttl = int(validated_token["exp"]) - int(time.time())
    if ttl > 0:
        cache.set(REVOKED_PREFIX + str(validated_token["jti"]), 1, timeout=ttl)


class CookieJWTAuthentication(JWTAuthentication):
    """JWT-аутентификация: токен берётся из заголовка Authorization
    или (если заголовка нет) из httpOnly-cookie. Отозванные при выходе
    access-токены отклоняются."""

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get(settings.AUTH_COOKIE_ACCESS)
        else:
            raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        if cache.get(REVOKED_PREFIX + str(validated_token["jti"])):
            raise InvalidToken("Токен отозван (выход из аккаунта).")
        return self.get_user(validated_token), validated_token
