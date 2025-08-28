from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApplicantViewSet, LoanApplicationViewSet

router = DefaultRouter()
router.register(r'applicants', ApplicantViewSet)
router.register(r'applications', LoanApplicationViewSet, basename='loanapplication')

urlpatterns = [
    path('', include(router.urls)),
]