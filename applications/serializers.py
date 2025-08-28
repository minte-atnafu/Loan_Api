from rest_framework import serializers
from .models import Applicant, LoanApplication

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ['id', 'name', 'email', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LoanApplicationSerializer(serializers.ModelSerializer):
    applicant_details = ApplicantSerializer(source='applicant', read_only=True)
    
    class Meta:
        model = LoanApplication
        fields = [
            'id', 'applicant', 'applicant_details', 'amount', 
            'risk_score', 'status', 'external_reference',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'risk_score', 'status', 'external_reference',
            'created_at', 'updated_at'
        ]


class LoanApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ['status']
        read_only_fields = ['id', 'applicant', 'amount', 'risk_score']


class ReportSummarySerializer(serializers.Serializer):
    total_applications = serializers.IntegerField()
    approved_applications = serializers.IntegerField()
    rejected_applications = serializers.IntegerField()
    pending_applications = serializers.IntegerField()
    manual_review_applications = serializers.IntegerField()
    approval_rate = serializers.FloatField()
    average_loan_amount = serializers.FloatField()