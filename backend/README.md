# HomeControl BaaS Backend

This is a custom Backend-as-a-Service (BaaS) for HomeControl, built with:
- **FastAPI** (High-performance API)
- **PostgreSQL** (Database)
- **Redis** (Caching/Realtime)
- **Docker** (Containerization)

## 🚀 How to Run

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.

### Start the Server
1. Open a terminal in the `backend` directory:
   ```bash
   cd backend
   ```
2. Run Docker Compose:
   ```bash
   docker-compose up --build
   ```
   This will start PostgreSQL, Redis, and the FastAPI backend.

3. The API will be available at: **http://localhost:8000**
4. Interactive Documentation (Swagger UI): **http://localhost:8000/docs**

## 🧪 Testing

1. Install test dependencies (locally):
   ```bash
   pip install httpx
   ```
2. Run the test script:
   ```bash
   python tests/test_flow.py
   ```

## 📂 Project Structure

- `app/main.py`: Entry point
- `app/api`: API Endpoints (Auth, Users, Devices)
- `app/db`: Database models and session
- `app/schemas`: Pydantic data models
