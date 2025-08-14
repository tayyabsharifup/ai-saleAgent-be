from rest_framework import serializers
from apps.users.models.lead_model import LeadModel, LeadPhoneModel, LeadEmailModel
from apps.users.models.agent_model import AgentModel
from apps.aiModule.models import ChatMessageHistory
from apps.aiModule.serializers import ChatMessageHistorySerializer


class LeadPhoneSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = LeadPhoneModel
        exclude = ('lead',)


class LeadEmailSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = LeadEmailModel
        exclude = ('lead',)


class LeadRegisterSerializer(serializers.ModelSerializer):
    lead_phone = LeadPhoneSerializer(
        many=True, required=False)
    lead_email = LeadEmailSerializer(
        many=True, required=False)
    assign_to = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = LeadModel
        fields = '__all__'

    def create(self, validated_data):
        lead_phones_data = validated_data.pop('lead_phone', [])
        lead_emails_data = validated_data.pop('lead_email', [])
        agent_email = validated_data.pop('assign_to', None)
        lead = LeadModel.objects.create(**validated_data)
        if agent_email:
            try:
                user = AgentModel.objects.get(user__email=agent_email)
                lead.assign_to = user
            except AgentModel.DoesNotExist:
                raise serializers.ValidationError(f"Agent with email {agent_email} not found.")
        for phone_data in lead_phones_data:
            LeadPhoneModel.objects.create(lead=lead, **phone_data)
        for email_data in lead_emails_data:
            LeadEmailModel.objects.create(lead=lead, **email_data)
        lead.save()
        return lead
    
    def update(self, instance, validated_data):
        lead_phones_data = validated_data.pop('lead_phone', None)
        lead_emails_data = validated_data.pop('lead_email', None)
        agent_email = validated_data.pop('assign_to', None)

        # Update LeadModel instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if agent_email:
            try:
                agent = AgentModel.objects.get(user__email=agent_email)
                instance.assign_to = agent
            except AgentModel.DoesNotExist:
                raise serializers.ValidationError(f"Agent with email {agent_email} not found.")

        instance.save()

        # Update related phones
        if lead_phones_data is not None:
            for phone_data in lead_phones_data:
                LeadPhoneModel.objects.create(lead=instance, **phone_data)

        # Update related emails
        if lead_emails_data is not None:
            for email_data in lead_emails_data:
                LeadEmailModel.objects.create(lead=instance, **email_data)

        return instance

    def validate_status(self, value):
        choices = ['in_progress', 'not_initiated', 'over_due', 'converted']
        if value not in choices:
            raise serializers.ValidationError(
                f'Value should be one of following: {", ".join(choices)}')
        else:
            return value

    def validate_assign_to(self, value):
        if not AgentModel.objects.filter(user__email = value):
            raise serializers.ValidationError(
                f'Agent do not exists with this Email')
        else:
            return value

class LeadListSerializer(serializers.ModelSerializer):
    lead_phone = LeadPhoneSerializer(source='leadphonemodel_set', many=True, required=False)
    lead_email = LeadEmailSerializer(source='leademailmodel_set', many=True, required=False)
    assign_to = serializers.StringRelatedField()

    class Meta:
        model = LeadModel
        fields = '__all__'