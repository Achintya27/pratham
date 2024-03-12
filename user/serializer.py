from rest_framework import serializers
from user.models import User, OTPModel
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    """
        User Serializer
        We modify the create method to set the password as hashed form
        & Used extra keyword args to hide the other details
    """
    class Meta:
        model = User
        fields = ("id", "is_staff", "is_active", "first_name", "last_name", "email", "password", 'country_name','company_name', 'company_address', 'designation')
        extra_kwargs = {'password': {'write_only': True},
                        'is_staff': {'read_only': True},
                        'id': {'read_only': True},
                        'is_active': {'read_only': True},
                        'updated_at': {'read_only': True},
                        'designation': {'required': False},
                        'company_address': {'required':False}
                        }


    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()
        return user





class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
        Token  Serializer
        Inherit the TokenObtainPairSerializer
        We modify the get_token (for change the last login)and validate data (for add somme extra response in token)
        & Used extra keyword args to hide the other details
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        user.last_login = timezone.now()
        user.save()
        # Add custom claims
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add your extra responses here
        data['email'] = self.user.email
        data['name'] = self.user.first_name
        data['id'] = str(self.user.id)
        data['is_staff'] = self.user.is_staff
        data['is_superuser'] = self.user.is_superuser
        return data
