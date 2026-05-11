from rest_framework import serializers

from .models import DrowsinessLog


class DrowsinessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrowsinessLog
        fields = ['id', 'timestamp', 'status', 'ear_value']
        read_only_fields = ['id', 'timestamp']
