from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from utils.utils import get_upload_path


class UserQuerySet(models.query.QuerySet):
    def all(self):
        return self.filter(is_active=True)


class UserManager(BaseUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given, email, and password.
        """
        if not username:
            raise ValueError('Username must be nonempty')
        if not email:
            raise ValueError('Email must be nonempty')

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        is_staff = extra_fields.get('is_staff')
        is_superuser = extra_fields.get('is_superuser')

        if is_staff is not True:
            raise ValueError('is_staff must be True')
        if is_superuser is not True:
            raise ValueError('is_superuser must be True')

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    MANAGER = _('manager')
    DISTRIBUTOR = _('distributor')
    CUSTOMER = _('customer')

    USER_TYPE = (
        (DISTRIBUTOR, _('Distributor')),
        (CUSTOMER, _('Customer'))
    )

    username = models.CharField(_('Username'),
                                max_length=150,
                                unique=True,
                                validators=[username_validator],
                                error_messages={'unique': _('The username is already exists')})

    email = models.CharField(_('Email'), max_length=255, unique=True)
    first_name = models.CharField(_('First Name'), max_length=150)
    last_name = models.CharField(_('Last Name'), max_length=150)
    date_joined = models.DateTimeField(_('Date Joined'), default=timezone.now)

    is_active = models.BooleanField(_('Active Status'),
                                    default=True,
                                    help_text=_('Designates whether this user account should be '
                                                'considered active. Set this flag to False instead of '
                                                'deleting accounts.'))

    is_staff = models.BooleanField(_('Staff Status'),
                                   default=False,
                                   help_text=_('Designates whether this user can access the admin site.'))

    is_superuser = models.BooleanField(_('Superuser Status'),
                                       default=False,
                                       help_text=_('Designates that this user '
                                                   'has all permissions without explicitly assigning them.'))

    type = models.CharField(_('Register as'), max_length=100, choices=USER_TYPE, default=CUSTOMER)
    image = models.ImageField(upload_to=get_upload_path,
                              width_field='width_field',
                              height_field='height_field',
                              null=True,
                              blank=True)

    width_field = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name='Image Width')
    height_field = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name='Image Height')

    # addresses       = models.ManyToManyField('address.Address', blank=True, related_name='user_addresses')
    # shipping        = models.ForeignKey('address.Address', related_name='+', blank=True, null=True, on_delete=models.SET_NULL)
    # billing         = models.ForeignKey('address.Address', related_name='+', blank=True, null=True, on_delete=models.SET_NULL)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def is_distributor(self):
        if self.type == self.DISTRIBUTOR:
            return True
        return False

    def is_approved(self):
        return self.distributor.is_approved

    def get_full_name(self):
        fullname = '{0} {1}'.format(self.first_name, self.last_name)
        if not fullname.strip():
            fullname = self.username
        return fullname.strip()

    def get_short_name(self):
        first_name = self.first_name
        if not first_name:
            first_name = self.username
        return first_name

    def get_image_url(self):
        url = settings.STATIC_URL + 'ecommerce/img/defaults/profile.jpg'
        if self.image:
            url = self.image.url
        return url

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])


class Distributor(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, primary_key=True)
    is_approved = models.BooleanField(default=False,
                                      verbose_name=_('Approve Status'),
                                      help_text=('Designates whether current status of this user '
                                                 'approved by any admin'))

    class Meta:
        verbose_name = _('Distributor')
        verbose_name_plural = _('Distributors')

    def __str__(self):
        return self.user.username
