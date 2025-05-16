# Duso API

A FastAPI-based backend API for the Duso mobile app.

## Features

- FastAPI framework
- MongoDB database integration
- User authentication and management
- RESTful API endpoints
- CORS support
- Environment-based configuration

## Prerequisites

- Python 3.8+
- MongoDB
- Virtual environment (recommended)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd duso-api
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=duso_db
SECRET_KEY=your-secret-key
```

## Running the Application

1. Start MongoDB:
```bash
mongod
```

2. Run the FastAPI application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

### Users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user

## Development

The project structure follows a clean architecture pattern:
```
app/
├── api/            # API endpoints
├── core/           # Core functionality
├── models/         # Data models
├── repositories/   # Database repositories
├── services/       # Business logic
└── main.py         # Application entry point
```