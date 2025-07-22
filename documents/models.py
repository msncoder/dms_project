# from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
# from django.db import models

# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ('superadmin', 'Super Admin'),
#         ('admin', 'Admin'),
#         ('editor', 'Editor'),
#     )
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='editor')

#     # Fix reverse accessor conflict
#     groups = models.ManyToManyField(
#         Group,
#         related_name='customuser_set',  # ✅ change this
#         blank=True,
#         help_text=(
#             'The groups this user belongs to. A user will get all permissions '
#             'granted to each of their groups.'
#         ),
#         verbose_name='groups',
#     )

#     user_permissions = models.ManyToManyField(
#         Permission,
#         related_name='customuser_set',  # ✅ change this too
#         blank=True,
#         help_text='Specific permissions for this user.',
#         verbose_name='user permissions',
#     )


# class Document(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     category = models.CharField(max_length=100)
#     file = models.FileField(upload_to='documents/')
#     summary = models.TextField(blank=True, null=True)
#     extracted_text = models.TextField(blank=True, null=True)
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title


import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models

# 🔸 Step 1: Custom Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('role', 'editor')  # Default role
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'superadmin')  # Superuser role

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

# 🔸 Step 2: Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('editor', 'Editor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='editor')

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        verbose_name='groups',
        help_text='Groups this user belongs to.'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

    # 👇 Assign custom manager
    objects = CustomUserManager()


# 🔸 Step 3: Document model
# class Document(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     category = models.CharField(max_length=100)
#     file = models.FileField(upload_to='documents/')
#     summary = models.TextField(blank=True, null=True)
#     extracted_text = models.TextField(blank=True, null=True)
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title



# Add this on top or below the models
import uuid

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'documents/{instance.user.id}/{uuid.uuid4()}.{ext}'

# Inside Document model:
class Document(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    
    # 👇 Updated
    file = models.FileField(upload_to=user_directory_path)

    summary = models.TextField(blank=True, null=True)
    extracted_text = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
