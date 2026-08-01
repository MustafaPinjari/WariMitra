from rest_framework import serializers
from .models import PilgrimProfile, FamilyGroup, EmergencyContact, LiveLocation


class PilgrimProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PilgrimProfile
        fields = '__all__'


class FamilyGroupSerializer(serializers.ModelSerializer):
    owner_username = serializers.SerializerMethodField(read_only=True)
    member_count = serializers.SerializerMethodField(read_only=True)
    members_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FamilyGroup
        fields = ['id', 'name', 'owner', 'owner_username', 'invite_code', 'member_count', 'members_details', 'created_at']
        read_only_fields = ['id', 'owner', 'invite_code', 'created_at']

    def get_owner_username(self, obj):
        return obj.owner.get_full_name() or obj.owner.username if obj.owner else 'Unknown'

    def get_member_count(self, obj):
        return obj.members.count()

    def get_members_details(self, obj):
        return [
            {
                'id': m.id,
                'username': m.username,
                'full_name': m.get_full_name() or m.username,
                'phone_number': getattr(m, 'phone_number', '') or '',
            }
            for m in obj.members.all()
        ]


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = '__all__'


class LiveLocationSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LiveLocation
        fields = ['user', 'username', 'full_name', 'latitude', 'longitude', 'updated_at', 'battery_level']
        read_only_fields = ['user', 'username', 'full_name', 'updated_at']

    def get_username(self, obj):
        return obj.user.username

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class UpdateLocationSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    battery_level = serializers.IntegerField(required=False, min_value=0, max_value=100)
