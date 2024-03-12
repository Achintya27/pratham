from django.db import models
from django.contrib.auth import models as auth_models
from uuid import uuid4
from utility.field import UnixTimestampField
from utility.malicious_validator import validate_no_malicious_content, Min_ValLen, Password_Validation
# Create your models here.

class UserManagerObject(auth_models.BaseUserManager):
    # Creating Normal User
    def create_user(self, email, password, **extraField):
        user = self.model(email = self.normalize_email(email), **extraField)
        user.set_password(password)
        user.is_active = False
        user.save(using=self._db)
        return user
    # Creating Super users
    def create_superuser(self, email, password, **extraField):
        extraField.setdefault('is_staff', True)
        extraField.setdefault('is_superuser', True)
        extraField.setdefault('is_active', True)

        if extraField.get('is_staff') is not True:
            raise ValueError(_('Super user must have the is_staff= True'))
        if extraField.get('is_superuser') is not True:
            raise ValueError(_('Super user must have the is_superuser= True'))
        return self.create_user(email,password, **extraField)



class User(auth_models.AbstractUser, auth_models.PermissionsMixin):
    """
            User  Model
             : Inherit the user from auth_models and its permission
             : customize the table name with meta Class db_table name
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, validators=[validate_no_malicious_content, Min_ValLen])
    last_name = models.CharField(max_length=255, validators=[validate_no_malicious_content, Min_ValLen])
    password = models.CharField(max_length=255, validators=[Password_Validation])
    country_name = models.CharField(max_length = 128, validators=[validate_no_malicious_content, Min_ValLen])
    company_name = models.CharField(max_length=255,validators=[validate_no_malicious_content, Min_ValLen])
    company_address = models.CharField(max_length=255,validators=[validate_no_malicious_content, Min_ValLen])
    designation = models.CharField(max_length=255, blank=True, validators=[validate_no_malicious_content])
    username = models.CharField(max_length=255, validators=[validate_no_malicious_content])
    created_at = UnixTimestampField(auto_now_add= True)
    updated_at = UnixTimestampField(auto_now =True)
    objects = UserManagerObject()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password', 'company_name', 'company_address']

    def __str__(self):
        return (self.email)

    class Meta:
        db_table = "user"


    def clean(self):
        super().clean()




class OTPModel(models.Model):
    """
        OTP  Model
        : customize the table name with meta Class db_table name
    """
    opt_id = models.AutoField(primary_key = True)
    user = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)

    class Meta:
        db_table = 'otp'
