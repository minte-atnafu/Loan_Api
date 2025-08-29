# Loan Application & Risk Scoring API

## 🎯 Overview

A Django REST Framework API for a microfinance company that processes loan applications with automated risk scoring. The system evaluates applications using a risk scoring service and automatically approves, rejects, or flags applications for manual review based on risk thresholds.

## 📊 Architecture Diagram

### System Architecture & Data Flow
```
┌─────────────────┐    HTTP/HTTPS     ┌─────────────────┐    Database    ┌─────────────┐
│   Client        │ ─────────────────► │   Django        │ ──────────────► │   PostgreSQL│
│   (Frontend/App)│                    │   REST API      │                │             │
└─────────────────┘                    └─────────────────┘                └─────────────┘
         │                                     │                                    │
         │                                     │                                    │
         │                                     ▼                                    │
         │                            ┌──────────────────┐                         │
         │                            │   Risk Scoring   │                         │
         │                            │   Service        │                         │
         │                            │   (Mock/External)│                         │
         │                            └──────────────────┘                         │
         │                                     │                                    │
         │                                     │                                    │
         │                                     ▼                                    │
         └───────────────────────────────── Response ───────────────────────────────┘

### Data Flow Sequence:
1. Client → POST /api/applications/ → Django API
2. Django API → Risk Scoring Service → Get Risk Score
3. Django API → Auto-decision based on risk score
4. Django API → Store application in database
5. Django API → Return response to client
```

## ⭐ Features

- **Loan Application Management**: Complete CRUD operations for loan applications
- **Automated Risk Scoring**: Integration with external risk assessment service
- **Auto-Decision Engine**: Automatic approval/rejection based on risk thresholds
- **Comprehensive Reporting**: Analytics and summary endpoints
- **RESTful API**: Clean, standardized API structure
- **Database Optimization**: Proper indexing and query optimization

## 🛠 Technology Stack

- **Backend Framework**: Django 4.x + Django REST Framework
- **Database**: PostgreSQL (with MySQL compatibility)
- **Authentication**: JWT Tokens + Basic Authentication
- **Caching**: Redis (for risk score caching)
- **API Documentation**: OpenAPI/Swagger-ready
- **Containerization**: Docker + Docker Compose

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL or MySQL
- Redis (optional, for caching)
- Docker (optional, for containerization)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone (https://github.com/minte-atnafu/Loan_Api)
   cd loan-application-api
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

### Docker Setup (Alternative)

1. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## 📡 API Endpoints

### Loan Applications
- `GET /api/applications/` - List all applications
- `POST /api/applications/` - Create new application
- `GET /api/applications/{id}/` - Get application details
- `PATCH /api/applications/{id}/update_status/` - Update application status
- `GET /api/applications/summary/` - Get application statistics

### Applicants
- `GET /api/applicants/` - List all applicants
- `POST /api/applicants/` - Create new applicant
- `GET /api/applicants/{id}/` - Get applicant details

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Example Request
```bash
curl -X POST http://localhost:8000/api/applications/ \
  -H "Content-Type: application/json" \
  -d '{
    "applicant": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "555-1234"
    },
    "amount": 15000
  }'
```

## 💡 Design Decisions & Trade-offs

### 1. Database Choice: PostgreSQL
- **Decision**: Used PostgreSQL as primary database
- **Rationale**: Better JSON support, reliability, and performance for financial data
- **Trade-off**: More complex setup than SQLite but better for production
- **Alternative**: MySQL support maintained through configuration

### 2. Risk Scoring Integration
- **Decision**: Implemented mock risk scoring service with fallback mechanism
- **Rationale**: Ensures system works without external dependencies during development
- **Trade-off**: Mock service doesn't reflect real-world risk patterns but provides consistency
- **Alternative**: Can easily switch to real external API by changing configuration

### 3. Authentication Strategy
- **Decision**: Implemented multiple authentication methods (JWT, Basic Auth, Session)
- **Rationale**: Flexibility for different client types (web, mobile, third-party)
- **Trade-off**: Increased complexity but better interoperability

### 4. Auto-Approval Logic
- **Decision**: Conservative threshold-based auto-approval system
- **Rationale**: Reduces risk while maintaining automation benefits
- **Thresholds**:
  - Score < 30: Auto-approved
  - Score 30-70: Manual review
  - Score > 70: Auto-rejected
- **Trade-off**: Some applications require manual intervention

### 5. Caching Strategy
- **Decision**: Implemented Redis caching for risk scores
- **Rationale**: Reduces external API calls and improves performance
- **Trade-off**: Adds infrastructure dependency but significantly improves efficiency

### 6. Error Handling
- **Decision**: Comprehensive error handling with fallback mechanisms
- **Rationale**: Ensures system resilience during external service failures
- **Trade-off**: More complex code but better user experience

### 7. API Design
- **Decision**: RESTful design with proper HTTP status codes
- **Rationale**: Standardized interface for frontend and third-party integration
- **Trade-off**: More structured approach requires stricter adherence to standards

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test applications

# Run with coverage
coverage run manage.py test applications
coverage report

# Run specific test
python manage.py test applications.tests.test_views
```

### Test Coverage
- Unit tests for models and services
- Integration tests for API endpoints
- Mock testing for external API integration
- Error scenario testing

## 🌐 Deployment

### Production Considerations
1. **Set `DEBUG=False`** in production environment
2. **Use proper database credentials** with limited permissions
3. **Configure HTTPS** for all communications
4. **Set up monitoring and logging**
5. **Implement rate limiting** for API endpoints
6. **Regular database backups**

### Environment Variables for Production
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DB_NAME=loanapp_prod
DB_USER=loanapp_user
DB_PASSWORD=secure-password
DB_HOST=production-db-host
DB_PORT=5432
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
RISK_SERVICE_URL=https://real-risk-api.com/score
RISK_SERVICE_API_KEY=your-api-key
```

## 📈 Performance Optimization

1. **Database indexing** on frequently queried fields
2. **Query optimization** with `select_related` and `prefetch_related`
3. **Redis caching** for frequently accessed data
4. **Pagination** for large datasets
5. **Compression** for API responses

## 🔒 Security Measures

1. **SQL injection protection** through Django ORM
2. **XSS protection** with Django's built-in security
3. **CSRF protection** for session-based authentication
4. **JWT token expiration** and refresh mechanisms
5. **Input validation** at both serializer and model levels
6. **Environment-based configuration** for sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## 🆘 Support

For issues and questions:
1. Check API documentation
2. Review existing issues
3. Create a new issue with detailed description

---

**Note**: This project demonstrates a production-ready loan application system with proper architecture patterns, security considerations, and scalability features. The mock risk scoring service can be easily replaced with a real external API when needed.