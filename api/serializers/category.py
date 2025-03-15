from rest_framework import serializers

from account.models import Category, Church, YouthGroup


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']
        



class ChurchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Church
        fields = ['id','name']
        




class YouthGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouthGroup
        fields = ['id','name']
        