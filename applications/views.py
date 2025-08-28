from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db import transaction
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import Applicant, LoanApplication
from .serializers import (
    ApplicantSerializer, 
    LoanApplicationSerializer,
    LoanApplicationStatusSerializer,
    ReportSummarySerializer
)
from .services import RiskScoringService

class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'id'


class LoanApplicationViewSet(viewsets.ModelViewSet):
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = LoanApplication.objects.select_related('applicant').all()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
            
        return queryset
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new loan application with automatic risk scoring
        """
        applicant_data = request.data.get('applicant', {})
        amount = request.data.get('amount')
        
        # Validate required fields
        if not applicant_data or not amount:
            return Response(
                {'error': 'Applicant data and amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not applicant_data.get('email'):
            return Response(
                {'error': 'Email is required in applicant data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check if applicant exists, create if not
            applicant, created = Applicant.objects.get_or_create(
                email=applicant_data['email'],
                defaults={
                    'name': applicant_data.get('name', ''),
                    'phone': applicant_data.get('phone', '')
                }
            )
            
            # Update applicant details if they already existed
            if not created:
                update_fields = []
                if 'name' in applicant_data and applicant_data['name'] != applicant.name:
                    applicant.name = applicant_data['name']
                    update_fields.append('name')
                if 'phone' in applicant_data and applicant_data['phone'] != applicant.phone:
                    applicant.phone = applicant_data['phone']
                    update_fields.append('phone')
                
                if update_fields:
                    applicant.save(update_fields=update_fields)
            
            # Create loan application
            application = LoanApplication.objects.create(
                applicant=applicant,
                amount=amount,
                status=LoanApplication.STATUS_PENDING
            )
            
            # Get risk score from service
            risk_score = RiskScoringService.get_risk_score(
                {
                    'name': applicant.name,
                    'email': applicant.email,
                    'phone': applicant.phone
                },
                amount
            )
            application.risk_score = risk_score
            
            # Auto-decision logic based on risk score
            if risk_score < 30:
                application.status = LoanApplication.STATUS_APPROVED
            elif risk_score > 70:
                application.status = LoanApplication.STATUS_REJECTED
            else:
                application.status = LoanApplication.STATUS_MANUAL_REVIEW
                
            application.save()
            
            serializer = self.get_serializer(application)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Failed to create application: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update application status (for manual review cases)
        """
        try:
            application = self.get_object()
            
            # Only allow status updates for manual review applications
            if application.status != LoanApplication.STATUS_MANUAL_REVIEW:
                return Response(
                    {'error': 'Only manual review applications can be updated'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = LoanApplicationStatusSerializer(application, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except LoanApplication.DoesNotExist:
            return Response(
                {'error': 'Application not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get comprehensive summary statistics of all applications
        /api/applications/summary/
        """
        # Get counts for each status
        status_counts = LoanApplication.objects.values('status').annotate(
            count=Count('id')
        )
        
        # Calculate summary data
        total = LoanApplication.objects.count()
        approved = LoanApplication.objects.filter(status=LoanApplication.STATUS_APPROVED).count()
        rejected = LoanApplication.objects.filter(status=LoanApplication.STATUS_REJECTED).count()
        pending = LoanApplication.objects.filter(status=LoanApplication.STATUS_PENDING).count()
        manual_review = LoanApplication.objects.filter(status=LoanApplication.STATUS_MANUAL_REVIEW).count()
        
        # Calculate additional statistics
        approval_rate = round((approved / total * 100), 2) if total > 0 else 0
        avg_loan_amount = LoanApplication.objects.aggregate(avg=Avg('amount'))['avg'] or 0
        
        # Recent activity (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_applications = LoanApplication.objects.filter(
            created_at__gte=seven_days_ago
        ).count()
        
        summary_data = {
            'total_applications': total,
            'approved_applications': approved,
            'rejected_applications': rejected,
            'pending_applications': pending,
            'manual_review_applications': manual_review,
            'approval_rate': approval_rate,
            'average_loan_amount': float(avg_loan_amount),
            'recent_applications_7_days': recent_applications,
            'timestamp': timezone.now().isoformat()
        }
        
        serializer = ReportSummarySerializer(summary_data)
        return Response(serializer.data)