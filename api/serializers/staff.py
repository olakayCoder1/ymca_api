from rest_framework import serializers

from api.models import StaffMember


class StaffMemberSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = StaffMember
        fields = ['id', 'name', 'position', 'category', 'image', 'order', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if instance.image:
            relative_url = instance.image.url
            if request is not None:
                data['image'] = request.build_absolute_uri(relative_url)
            else:
                data['image'] = relative_url
        else:
            data['image'] = None

        return data