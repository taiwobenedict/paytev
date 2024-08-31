from rest_framework import serializers

class HusmoDataAPISerializer(serializers.Serializer):
    network = serializers.CharField(max_length=50)
    amount = serializers.FloatField()
    mobile_number = serializers.CharField(max_length=15)
    airtime_type = serializers.CharField(default='VTU')
    Ported_number = serializers.CharField(default='false')
