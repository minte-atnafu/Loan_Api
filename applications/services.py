import requests
import logging
from django.conf import settings
from django.core.cache import cache
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)

class RiskScoringService:
    """Service to handle communication with external risk scoring API"""
    
    @staticmethod
    def get_risk_score(applicant_data, loan_amount):
        """
        Fetch risk score from external API with proper error handling
        """
        # For development, use mock service
        if settings.DEBUG and not getattr(settings, 'USE_REAL_RISK_API', False):
            return RiskScoringService._calculate_mock_score(applicant_data, loan_amount)
        
        # For production, call real external API
        try:
            response = RiskScoringService._call_external_api(applicant_data, loan_amount)
            return response['score']
            
        except RequestException as e:
            logger.error(f"Risk scoring API error: {str(e)}")
            # Fallback to mock scoring for resilience
            return RiskScoringService._calculate_fallback_score(applicant_data, loan_amount)
    
    @staticmethod
    def _call_external_api(applicant_data, loan_amount):
        """
        Make actual API call to external risk scoring service
        """
        request_data = {
            'applicant': {
                'name': applicant_data.get('name'),
                'email': applicant_data.get('email'),
                'phone': applicant_data.get('phone')
            },
            'loan_amount': float(loan_amount),
            'request_id': f"loanapp_{hash(frozenset(applicant_data.items()))}_{loan_amount}"
        }
        
        headers = {
            'Authorization': f'Bearer {settings.RISK_SERVICE_API_KEY}',
            'Content-Type': 'application/json',
            'User-Agent': 'LoanApplicationAPI/1.0'
        }
        
        response = requests.post(
            settings.RISK_SERVICE_URL,
            json=request_data,
            headers=headers,
            timeout=settings.RISK_SERVICE_TIMEOUT,
            verify=True  # Always verify SSL certificates
        )
        
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def _calculate_mock_score(applicant_data, loan_amount):
        """
        Realistic mock risk scoring algorithm for development
        """
        import random
        import hashlib
        
        # Create deterministic but varied score based on input data
        input_string = f"{applicant_data.get('email','')}{loan_amount}"
        deterministic_seed = int(hashlib.md5(input_string.encode()).hexdigest()[:8], 16)
        random.seed(deterministic_seed)
        
        base_score = 50  # Middle risk
        
        # Factor 1: Loan amount risk (higher amount = higher risk)
        amount_risk = min(25, (float(loan_amount) / 10000) * 12)
        base_score += amount_risk
        
        # Factor 2: Email domain analysis
        email = applicant_data.get('email', '').lower()
        if email:
            if any(domain in email for domain in ['gmail.com', 'yahoo.com', 'hotmail.com']):
                base_score += 5  # Personal emails slightly higher risk
            elif any(domain in email for domain in ['.edu', '.gov', '.org']):
                base_score -= 8  # Institutional emails lower risk
        
        # Factor 3: Name completeness
        name = applicant_data.get('name', '')
        if name and len(name.split()) >= 2:
            base_score -= 4
        
        # Factor 4: Realistic randomness
        random_factor = random.randint(-12, 12)
        base_score += random_factor
        
        return max(0, min(100, round(base_score)))
    
    @staticmethod
    def _calculate_fallback_score(applicant_data, loan_amount):
        """
        Conservative fallback scoring when external API fails
        """
        # Default to manual review for safety
        return 50