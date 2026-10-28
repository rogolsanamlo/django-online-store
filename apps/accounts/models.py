from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from utils import FileUploud


class CustomUserManager(BaseUserManager):
    def create_user(self, mobile_number, email='', name='', family='', active_code=None,
                    gender=None, password=None):
        if not mobile_number:
            raise ValueError('شماره موبایل باید وارد شود')
        user = self.model(
            mobile_number=mobile_number,
            email=self.normalize_email(email),
            name=name,
            family=family,
            active_code=active_code,
            gender=gender,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, email, name, family, password=None,
                         active_code=None, gender=None):
        user = self.create_user(
            mobile_number=mobile_number,
            email=email,
            name=name,
            family=family,
            active_code=active_code,
            gender=gender,
            password=password,
        )
        user.is_active = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [('True', 'مرد'), ('False', 'زن')]

    name = models.CharField('نام', max_length=50, blank=True)
    family = models.CharField('نام خانوادگی', max_length=50, blank=True)
    email = models.EmailField('ایمیل', max_length=200, blank=True)
    mobile_number = models.CharField('شماره موبایل', max_length=11, unique=True)
    gender = models.CharField(
        'جنسیت', max_length=50, blank=True, null=True, choices=GENDER_CHOICES, default='True'
    )
    register_date = models.DateField('تاریخ ثبت نام', default=timezone.now)
    is_active = models.BooleanField('فعال', default=False)
    active_code = models.CharField('کد فعال سازی', max_length=100, blank=True, null=True)
    is_admin = models.BooleanField('مدیر سایت', default=False)

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['email', 'name', 'family']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.get_full_name() or self.mobile_number

    def get_full_name(self):
        return f'{self.name} {self.family}'.strip()

    @property
    def is_staff(self):
        return self.is_admin


class Customer(models.Model):
    file_upload = FileUploud('images', 'customer')

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, verbose_name='کاربر'
    )
    phone_number = models.CharField('شماره تلفن', max_length=11, null=True, blank=True)
    address = models.TextField('آدرس', null=True, blank=True)
    image_name = models.ImageField(
        'تصویر پروفایل', upload_to=file_upload, null=True, blank=True
    )

    class Meta:
        verbose_name = 'مشتری'
        verbose_name_plural = 'مشتریان'

    def __str__(self):
        return str(self.user)
