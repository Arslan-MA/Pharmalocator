from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to='images/users/', default='images/users/default_user.jpg',
                              blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_courier = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"Email: {self.email} - Staff status: {self.is_staff} - Courier status: {self.is_courier}"


class MedicineCategory(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class TypeMedicine(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Medicine(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=True, blank=True)
    photo = models.ImageField(upload_to='images/products/')
    medicinal_category = models.ForeignKey(MedicineCategory, on_delete=models.CASCADE)
    type_medicine = models.ForeignKey(TypeMedicine, on_delete=models.CASCADE)

    AGE_CATEGORY_CHOICE = [
        ('для детей', 'для детей'),
        ('для взрослых', 'для взрослых'),
        ('для пожилых', 'для пожилых'),
    ]

    age_category = models.CharField(max_length=255, choices=AGE_CATEGORY_CHOICE)
    description = models.TextField()
    price = models.PositiveIntegerField()

    def get_absolute_url(self):
        return reverse('medicine_slug', args=(self.slug,))

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        str_ = f"{self.title}_{self.medicinal_category}-{self.price}"
        self.slug = slugify(str_)
        super(Medicine, self).save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f"{self.title} - {self.medicinal_category.title} - {self.age_category} - {self.price}"


class Pharmacy(models.Model):
    name = models.CharField(max_length=255)
    pharmacist = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, blank=True, null=True)
    photo = models.ImageField(upload_to='images/pharmacy/', default='images/pharmacy/default_pharmacy.png')
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def get_absolute_url(self):
        return reverse('pharmacy_id', args=(self.pk,))

    def __str__(self):
        return f"{self.name} - {self.phone} - {self.address}"


class Like(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    disliked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('content_type', 'object_id', 'user')

    def __str__(self):
        return f"{self.content_type} - {self.object_id}"


class Dislike(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('content_type', 'object_id', 'user')

    def __str__(self):
        return f"{self.content_type} - {self.object_id}"


class MedicineComment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    published = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    likes = GenericRelation(Like)
    dislike = GenericRelation(Dislike)

    def __str__(self):
        return f"{self.user.name} - {self.subject.title}"
