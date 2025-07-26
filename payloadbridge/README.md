# PayloadBridge Microservice

A production-ready FastAPI microservice for secure, validated, and auditable order payload forwarding to RecVue’s Contract Orchestrator API.

## Features
- **Strict Pydantic validation** for all order payloads
- **Okta-based authentication** and RecVue /authorize integration
- **Robust error handling** with clear HTTP status codes
- **Centralized config** via environment variables
- **Structured logging** with request/tenant/correlation IDs
- **Dockerized** for easy deployment
- **Comprehensive tests** using pytest and respx

## Project Structure

```
payloadbridge/
├── main.py                   # FastAPI entry point
├── models/
│   └── order_line.py         # Pydantic validation model for order payloads
├── services/
│   └── auth_utils.py         # Handles /authorize authentication logic
├── core/
│   └── config.py             # Stores constants and base URLs
├── tests/
│   └── test_payloadbridge.py # Unit and integration tests
├── sample_data/
│   └── sample_payload.json   # Example payload for testing
├── requirements.txt          # Python dependencies
└── README.md                 # Setup and usage instructions
```

## Quickstart

1. **Clone the repo:**
   ```sh
   git clone https://github.com/rohitmenonrecvue/PayloadBridge_RecVue.git
   cd PayloadBridge_RecVue
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure environment:**
   - Copy `.env.example` to `.env` and fill in required values.
4. **Run the service:**
   ```sh
   uvicorn payloadbridge.main:app --reload
   ```
5. **Run tests:**
   ```sh
   pytest
   ```

## API Endpoints
- `POST /invoke_order_creation` — Validates, authenticates, and forwards order payloads
- `GET /healthcheck` — Service health status

## Testing
- See `tests/test_payloadbridge.py` for unit and integration tests
- Use `sample_data/sample_payload.json` for example payloads

## Docker
- Build: `docker build -t payloadbridge .`
- Run: `docker run --env-file .env -p 8000:8000 payloadbridge`

## License
MIT

## Testing
Run all tests:
```sh
pytest
```

## Folder Structure
- `app/main.py` - FastAPI entry point
- `app/api/routes.py` - API endpoints
- `app/models/order_line.py` - Pydantic models & validation
- `app/services/auth_utils.py` - Auth logic
- `app/core/config.py` - Config/constants
- `app/tests/` - Tests
- `sample_data/sample_payload.json` - Example payload
- `app/postman_collection.json` - Postman collection

## Postman Collection
Import `app/postman_collection.json` into Postman for ready-to-use API requests.

## References
- See `../docs/API_MANDATORY_FIELDS_GUIDE.md` and `../docs/ORDER_VALIDATION_DOCUMENTATION.md` for field rules.
# PayloadBridge Microservice

## Overview
PayloadBridge is a microservice built using FastAPI that facilitates the creation of orders by forwarding validated payloads to the RecVue API. This service is designed to handle incoming requests, validate the payloads, and ensure proper communication with external services.

## Directory Structure
The project follows a structured directory layout to separate concerns and enhance maintainability:

```
payloadbridge
├── app
│   ├── main.py               # Entry point of the FastAPI application
│   ├── api                   # API related functionalities
│   │   ├── __init__.py       # Initializes the API module
│   │   └── routes.py         # Defines API routes
│   ├── core                  # Core application settings
│   │   ├── __init__.py       # Initializes the core module
│   │   └── config.py         # Configuration settings
│   ├── models                # Data models for validation
│   │   ├── __init__.py       # Initializes the models module
│   │   └── payload.py        # Pydantic model for payload validation
│   ├── services              # Business logic and service layer
│   │   ├── __init__.py       # Initializes the services module
│   │   └── bridge.py         # Logic for API communication
│   └── tests                 # Test cases for the application
│       ├── __init__.py       # Initializes the tests module
│       └── test_routes.py     # Unit and integration tests
├── requirements.txt          # Project dependencies
├── README.md                 # Project documentation
└── .gitignore                # Files to ignore in version control
```

## Setup Instructions
1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd payloadbridge
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the FastAPI application, execute the following command:
```
uvicorn app.main:app --reload
```
This will start the server at `http://127.0.0.1:8000`, and you can access the API documentation at `http://127.0.0.1:8000/docs`.

## Testing
To run the tests, use the following command:
```
pytest app/tests
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.