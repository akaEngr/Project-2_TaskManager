from rest_framework import serializers
from django.contrib.auth.models import User
from .models import TaskModel

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["username", "password", "confirm_password"]

    def create(self, validated_data):
        confirm_password = validated_data.pop("confirm_password")
        return User.objects.create_user(**validated_data)
    
        
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()



class TaskSerializer(serializers.ModelSerializer):
    created_date = serializers.DateField(   #. IMP 
        format="%d-%m-%Y",
        read_only = True
    )
    created_time = serializers.TimeField(
        format="%I:%M:%S %p",
        read_only = True
    )
    class Meta:
        model = TaskModel
        fields = ["id", "title", "description", "is_completed", "user", "created_date", "created_time"]
        read_only_fields = ["id", "user"]