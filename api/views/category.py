from rest_framework import generics

from account.models import Category, Church, YouthGroup
from api.serializers.category import CategorySerializer, ChurchSerializer, YouthGroupSerializer
from api.utils.response.response_format import success_response



class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    

    def get(self, request, *args, **kwargs):
        serializers = self.serializer_class(
            self.get_queryset(), many=True)
        
        return success_response(data=serializers.data)
    



class ChurchListView(generics.ListAPIView):
    queryset = Church.objects.all()
    serializer_class = ChurchSerializer

    def get(self, request, *args, **kwargs):
        serializers = self.serializer_class(
            self.get_queryset(), many=True)
        return success_response(data=serializers.data)
    



class YouthGroupListView(generics.ListAPIView):
    queryset = YouthGroup.objects.all()
    serializer_class = YouthGroupSerializer

    def get(self, request, *args, **kwargs):
        serializers = self.serializer_class(
            self.get_queryset(), many=True)
        return success_response(data=serializers.data)