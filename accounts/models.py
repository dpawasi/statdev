from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.signals import user_logged_in
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from model_utils import Choices


@python_2_unicode_compatible
class Address(models.Model):
    """This model represents an Australian address (physical or mailing).
    """
    AU_STATE_CHOICES = Choices(
        (1, 'act', ('ACT')),
        (2, 'nsw', ('NSW')),
        (3, 'nt', ('NT')),
        (4, 'qld', ('QLD')),
        (5, 'sa', ('SA')),
        (6, 'tas', ('TAS')),
        (7, 'vic', ('VIC')),
        (8, 'wa', ('WA')),
    )
    line1 = models.CharField('Line 1', max_length=255)
    line2 = models.CharField('Line 2', max_length=255, blank=True, null=True)
    locality = models.CharField('Suburb / Town', max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, choices=AU_STATE_CHOICES, default=AU_STATE_CHOICES.wa, blank=True, null=True)
    postcode = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'addresses'

    def __str__(self):
        return self.summary()

    def summary(self):
        """Returns a single string summary of the address, separating fields using commas.
        """
        return ', '.join(self.active_address_fields())

    def active_address_fields(self):
        """Return non-empty components of the address.
        """
        fields = [self.line1, self.line2, self.locality, self.get_state_display(), self.postcode]
        return [str(f).strip() for f in fields if f]


class EmailUserManager(BaseUserManager):
    """A custom Manager for the EmailUser model.
    """
    use_in_migrations = True

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """Creates and saves an EmailUser with the given email and password.
        """
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email, is_staff=is_staff, is_superuser=is_superuser)
        user.extra_data = extra_fields
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


@python_2_unicode_compatible
class EmailUser(AbstractBaseUser, PermissionsMixin):
    """Custom authentication model for the statdev project.
    Password and email are required. Other fields are optional.
    """
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the admin site.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active.'
                  'Unselect this instead of deleting ledger.accounts.',
    )
    date_joined = models.DateTimeField(default=timezone.now)

    objects = EmailUserManager()
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    def get_short_name(self):
        if self.first_name:
            return self.first_name
        return self.email


@python_2_unicode_compatible
class EmailUserProfile(models.Model):
    """This model represents a 1-to-1 profile for an EmailUser object,
    containing additional information about a user.
    """
    emailuser = models.OneToOneField(EmailUser, editable=False)
    dob = models.DateField(null=True, blank=True, verbose_name='date of birth')
    # TODO: business logic related to identification file upload/changes.
    identification = models.FileField(upload_to='uploads/%Y/%m/%d', null=True, blank=True)
    id_verified = models.DateField(null=True, blank=True, verbose_name='ID verified')
    home_phone = models.CharField(max_length=50, null=True, blank=True)
    work_phone = models.CharField(max_length=50, null=True, blank=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)
    postal_address = models.ForeignKey(Address, related_name='user_postal_address', blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='user_billing_address', blank=True, null=True)

    class Meta:
        verbose_name = 'user profile'
        verbose_name_plural = 'user profiles'

    def __str__(self):
        return '{}'.format(self.emailuser.email)

    def get_absolute_url(self):
        return reverse('user_profile')


def get_user_profile(**kwargs):
    EmailUserProfile.objects.get_or_create(emailuser=kwargs['user'])

# Use user_logged_in signal to ensure that user profile exists
user_logged_in.connect(get_user_profile)


@python_2_unicode_compatible
class Organisation(models.Model):
    """This model represents the details of a company or other organisation.
    Management of these objects will be delegated to 0+ EmailUsers.
    """
    name = models.CharField(max_length=128)
    abn = models.CharField(max_length=50, null=True, blank=True)
    # TODO: business logic related to identification file upload/changes.
    identification = models.FileField(upload_to='uploads/%Y/%m/%d', null=True, blank=True)
    postal_address = models.ForeignKey(Address, related_name='org_postal_address', blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='org_billing_address', blank=True, null=True)
    # TODO: business logic related to delegate changes.
    delegates = models.ManyToManyField(EmailUserProfile, blank=True)

    def __str__(self):
        return self.name
