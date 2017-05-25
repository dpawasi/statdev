from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.signals import user_logged_in
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django_countries.fields import CountryField
import os


@python_2_unicode_compatible
class Address(models.Model):
    """This model represents an Australian address (physical or mailing).
    It is a near-duplicate of the ledger Address model.
    """
    STATE_CHOICES = (
        ('ACT', 'ACT'),
        ('NSW', 'NSW'),
        ('NT', 'NT'),
        ('QLD', 'QLD'),
        ('SA', 'SA'),
        ('TAS', 'TAS'),
        ('VIC', 'VIC'),
        ('WA', 'WA')
    )

    # Addresses consist of 1+ lines, only the first of which is required.
    line1 = models.CharField('Line 1', max_length=255)
    line2 = models.CharField('Line 2', max_length=255, blank=True)
    line3 = models.CharField('Line 3', max_length=255, blank=True)
    locality = models.CharField('Suburb / Town', max_length=255)
    state = models.CharField(max_length=255, choices=STATE_CHOICES, default='WA', blank=True)
    country = CountryField(default='AU')
    postcode = models.CharField(max_length=10)
    # A field only used for searching addresses.
    search_text = models.TextField(editable=False)

    def __str__(self):
        return self.summary

    class Meta:
        verbose_name_plural = 'addresses'

    def clean(self):
        # Strip all whitespace.
        for field in ['line1', 'line2', 'line3', 'locality', 'state']:
            if self.__dict__[field]:
                self.__dict__[field] = self.__dict__[field].strip()

    def save(self, *args, **kwargs):
        self._update_search_text()
        super(Address, self).save(*args, **kwargs)

    def _update_search_text(self):
        search_fields = filter(
            bool, [self.line1, self.line2, self.line3, self.locality,
                   self.state, str(self.country.name), self.postcode])
        self.search_text = ' '.join(search_fields)

    @property
    def summary(self):
        """Returns a single string summary of the address, separating fields using commas.
        """
        return u', '.join(self.active_address_fields())

    def active_address_fields(self):
        """Return the non-empty components of the address.
        """
        fields = [self.line1, self.line2, self.line3,
                  self.locality, self.state, self.country, self.postcode]
        fields = [str(f).strip() for f in fields if f]
        return fields

    def join_fields(self, fields, separator=u', '):
        """Join a sequence of fields using the specified separator.
        """
        field_values = []
        for field in fields:
            value = getattr(self, field)
            field_values.append(value)
        return separator.join(filter(bool, field_values))


@python_2_unicode_compatible
class Document(models.Model):
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='%Y/%m/%d')
    uploaded_date = models.DateTimeField(auto_now_add=True)

    @property
    def path(self):
        return self.file.path

    @property
    def filename(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename


class DocumentListener(object):
    """Event listener for Document model.
    """
    @staticmethod
    @receiver(post_delete, sender=Document)
    def _post_delete(sender, instance, **kwargs):
        # Pass false so FileField doesn't save the model.
        try:
            instance.file.delete(False)
        except:
            #  if deleting file is failed, ignore.
            pass

    @staticmethod
    @receiver(pre_save, sender=Document)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = Document.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=Document)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if original_instance and original_instance.file and instance.file != original_instance.file:
            # file changed, delete the original file
            try:
                original_instance.file.delete(False)
            except:
                # if deleting file is failed, ignore.
                pass
            delattr(instance, "_original_instance")


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
    first_name = models.CharField(max_length=128, blank=False, verbose_name='Given name(s)')
    last_name = models.CharField(max_length=128, blank=False)
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

    TITLE_CHOICES = (
        ('Mr', 'Mr'),
        ('Miss', 'Miss'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr')
    )
    title = models.CharField(max_length=100, choices=TITLE_CHOICES, null=True, blank=True,
                             verbose_name='title', help_text='')
    dob = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False,
                           verbose_name="date of birth", help_text='')
    phone_number = models.CharField(max_length=50, null=True, blank=True,
                                    verbose_name="phone number", help_text='')
    mobile_number = models.CharField(max_length=50, null=True, blank=True,
                                     verbose_name="mobile number", help_text='')
    fax_number = models.CharField(max_length=50, null=True, blank=True,
                                  verbose_name="fax number", help_text='')

    residential_address = models.ForeignKey(Address, null=True, blank=False, related_name='+')
    postal_address = models.ForeignKey(Address, null=True, blank=True, related_name='+')
    billing_address = models.ForeignKey(Address, null=True, blank=True, related_name='+')

    identification = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL, related_name='identification_document')

    senior_card = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL, related_name='senior_card')

    character_flagged = models.BooleanField(default=False)

    character_comments = models.TextField(blank=True)

    documents = models.ManyToManyField(Document)

    extra_data = JSONField(default=dict)

    objects = EmailUserManager()
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.get_full_name()

    def clean(self):
        super(EmailUser, self).clean()
        self.email = self.email.lower() if self.email else self.email

    def get_short_name(self):
        if self.first_name:
            return self.first_name
        return self.email

    def get_full_name(self):
        if self.first_name:
            return '{} {}'.format(self.first_name, self.last_name).strip()
        return self.email


@python_2_unicode_compatible
class Organisation(models.Model):
    """This model represents the details of a company or other organisation.
    Management of these objects will be delegated to 0+ EmailUsers.
    """
    name = models.CharField(max_length=128, unique=True)
    abn = models.CharField(max_length=50, null=True, blank=True, verbose_name='ABN')
    # TODO: business logic related to identification file upload/changes.
    identification = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL)
    postal_address = models.ForeignKey(Address, related_name='org_postal_address', blank=True, null=True, on_delete=models.SET_NULL)
    billing_address = models.ForeignKey(Address, related_name='org_billing_address', blank=True, null=True, on_delete=models.SET_NULL)
    # TODO: business logic related to delegate changes.
    delegates = models.ManyToManyField(EmailUser, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('organisation_detail', args=(self.pk,))
