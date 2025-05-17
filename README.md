# Credit-Based Image Processing SaaS

A SaaS application that allows users to process images using a credit-based system. Users can purchase credits and use them to process images with various effects.

## Features

- User authentication and authorization
- Credit-based system for image processing
- Secure payment integration with Razorpay
- Asynchronous image processing with Celery
- Modern UI with Next.js and TailwindCSS
- Docker containerization for easy deployment

## Prerequisites

- Docker and Docker Compose
- PostgreSQL (if running locally)
- Redis (if running locally)
- Razorpay account for payment processing

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd credit-based-saas
```

2. Create environment files:
```bash
# Backend
cp backend/.env.example backend/.env
# Frontend
cp frontend/.env.example frontend/.env
```

3. Update the environment variables:
- Set up PostgreSQL credentials
- Configure Redis connection
- Add Razorpay API keys
- Generate a secure SECRET_KEY

4. Build and start the containers:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development

### Backend

The backend is built with:
- FastAPI
- PostgreSQL
- Celery
- Redis
- Razorpay

To run the backend locally:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

The frontend is built with:
- Next.js
- TailwindCSS
- shadcn/ui
- Zustand

To run the frontend locally:
```bash
cd frontend
npm install
npm run dev
```

## API Documentation

The API documentation is available at `/docs` when running the backend server. It provides detailed information about all available endpoints, request/response schemas, and authentication requirements.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# App Configuration
SECRET_KEY=your-secret-key-here  # Generate a secure random key
API_V1_STR=/api/v1
PROJECT_NAME=Credit-Based Image Processing SaaS
VERSION=1.0.0

# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=your-postgres-username
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_DB=credit_saas_db

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Celery Configuration
CELERY_BROKER_URL=redis://:your-redis-password@localhost:6379/0
CELERY_RESULT_BACKEND=redis://:your-redis-password@localhost:6379/0

# Razorpay Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Storage Configuration
UPLOAD_DIR=uploads
PROCESSED_DIR=processed

# Credits Configuration
CREDITS_PER_TASK=1 