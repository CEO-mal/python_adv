from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

REGISTER = "/api/auth/register/"
LOGIN = "/api/auth/login/"
REFRESH = "/api/auth/refresh/"
LOGOUT = "/api/auth/logout/"
PASSWORD = "Kv7Rt2Wq9X"


class RegisterTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.data = {
            "username": "nadya",
            "email": "nadya@example.com",
            "password": PASSWORD,
            "password2": PASSWORD,
        }

    def test_register_success_and_password_is_hashed(self):
        response = self.client.post(REGISTER, self.data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.json())
        user = User.objects.get(username="nadya")
        self.assertNotEqual(user.password, PASSWORD)   # в БД не сам пароль
        self.assertTrue(user.password.startswith("pbkdf2_"))  # а его хэш
        self.assertTrue(user.check_password(PASSWORD))

    def test_register_duplicate_username_and_email(self):
        self.client.post(REGISTER, self.data, format="json")
        same_login = dict(self.data, username="NADYA", email="other@example.com")
        r1 = self.client.post(REGISTER, same_login, format="json")
        self.assertEqual(r1.status_code, 400)
        self.assertIn("username", r1.json())
        same_email = dict(self.data, username="other", email="NADYA@example.com")
        r2 = self.client.post(REGISTER, same_email, format="json")
        self.assertEqual(r2.status_code, 400)
        self.assertIn("email", r2.json())

    def test_register_weak_passwords(self):
        for weak in ("Short1A", "alllowercase1", "ALLUPPERCASE1", "NoDigitsHere"):
            data = dict(self.data, password=weak, password2=weak)
            response = self.client.post(REGISTER, data, format="json")
            self.assertEqual(response.status_code, 400, weak)
            self.assertIn("password", response.json(), weak)

    def test_register_password_mismatch(self):
        data = dict(self.data, password2="Another1Pass")
        response = self.client.post(REGISTER, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("password2", response.json())

    def test_register_invalid_email_and_missing_fields(self):
        response = self.client.post(REGISTER, dict(self.data, email="not-an-email"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json())
        empty = self.client.post(REGISTER, {}, format="json")
        self.assertEqual(empty.status_code, 400)
        for field in ("username", "email", "password", "password2"):
            self.assertIn(field, empty.json())


class LoginRefreshLogoutTests(APITestCase):
    def setUp(self):
        cache.clear()
        User.objects.create_user("nadya", "nadya@example.com", PASSWORD)

    def login(self):
        return self.client.post(LOGIN, {"username": "nadya", "password": PASSWORD}, format="json")

    def test_login_returns_tokens_and_httponly_cookies(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("access", body)
        self.assertIn("refresh", body)
        for name in ("access_token", "refresh_token"):
            self.assertIn(name, response.cookies)
            self.assertTrue(response.cookies[name]["httponly"])

    def test_login_wrong_password_unknown_user_and_missing_fields(self):
        wrong = self.client.post(LOGIN, {"username": "nadya", "password": "Bad1Password"}, format="json")
        self.assertEqual(wrong.status_code, 401)
        unknown = self.client.post(LOGIN, {"username": "ghost", "password": PASSWORD}, format="json")
        self.assertEqual(unknown.status_code, 401)
        missing = self.client.post(LOGIN, {"username": "nadya"}, format="json")
        self.assertEqual(missing.status_code, 400)

    def test_cookie_authentication_works_without_header(self):
        self.login()  # cookie сохраняется в тестовом клиенте
        self.assertEqual(self.client.get("/api/tasks/").status_code, 200)
        self.assertEqual(APIClient().get("/api/tasks/").status_code, 401)

    def test_refresh_rotates_and_blacklists_old_refresh(self):
        old_refresh = self.login().json()["refresh"]
        response = self.client.post(REFRESH, {"refresh": old_refresh}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        new_refresh = response.json()["refresh"]
        self.assertNotEqual(new_refresh, old_refresh)
        reuse = self.client.post(REFRESH, {"refresh": old_refresh}, format="json")
        self.assertEqual(reuse.status_code, 401)   # старый refresh аннулирован

    def test_logout_blacklists_tokens_and_deletes_cookies(self):
        tokens = self.login().json()
        response = self.client.post(LOGOUT, {}, format="json")  # refresh берётся из cookie
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertEqual(response.cookies["refresh_token"].value, "")
        self.assertEqual(BlacklistedToken.objects.count(), 1)  # refresh в чёрном списке

        again = APIClient().post(REFRESH, {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(again.status_code, 401)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
        self.assertEqual(client.get("/api/tasks/").status_code, 401)  # access отозван

    def test_logout_requires_refresh_token(self):
        response = APIClient().post(LOGOUT, {}, format="json")
        self.assertEqual(response.status_code, 400)
