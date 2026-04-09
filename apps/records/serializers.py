from rest_framework import serializers
from apps.records.models import Attempt

class AttemptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attempt
        fields = ['user', 'node', 'date', 'attempt']