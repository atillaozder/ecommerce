from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Q

try:
    am = settings.AUTHENTICATION_METHOD
except:
    am = 'both'
try:
    cs = settings.AUTHENTICATION_CASE_SENSITIVE
except:
    cs = 'email'

VALID_AM = ['username', 'email', 'both']
VALID_CS = ['username', 'email', 'both', 'none']

if (am not in VALID_AM):
    raise Exception("Invalid value for AUTHENTICATION_METHOD in project "
                    "settings. Use 'username','email', or 'both'.")

if (cs not in VALID_CS):
    raise Exception("Invalid value for AUTHENTICATION_CASE_SENSITIVE in project "
                    "settings. Use 'username','email', 'both' or 'none'.")

class DualAuthentication(ModelBackend):
    """
    Authentication backend which allows users to authenticate using either their
    username or email address
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()

        if username is None:
            username = kwargs.get(user_model.USERNAME_FIELD)

        # The `username` field is allows to contain `@` characters so
        # technically a given email address could be present in either field,
        # possibly even for different users, so we'll query for all matching
        # records and test each one.
        users = user_model._default_manager.filter(
            Q(**{user_model.USERNAME_FIELD: username}) | Q(email__iexact=username)
        )

        # Test whether any matched user has the provided password:
        for user in users:
            if user.check_password(password):
                return user
        if not users:
            user_model().set_password(password)

    def get_user(self, username):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=username)
        except UserModel.DoesNotExist:
            return None
