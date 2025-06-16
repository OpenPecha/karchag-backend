Buddhist Digital Library API
🏃 Running the Backend Locally
Follow these steps to set up and run the server:
1️⃣ Clone the Repo
bashgit clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
2️⃣ Create a Virtual Environment
bashpython -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
3️⃣ Install Dependencies
bashpip install -r requirements.txt
4️⃣ Database Setup
Option A: SQLite (Default - Quick Start)
No additional setup required. The app will create a SQLite database automatically.
Option B: PostgreSQL (Production)
Create a .env file in the root directory and add:
envDATABASE_URL=postgresql://username:password@localhost:5432/your_db
ENVIRONMENT=production
5️⃣ Start the Development Server
uvicorn main:app --reload
📌 API Documentation – Swagger UI
This API follows the OpenAPI specification and provides interactive documentation via Swagger UI.
Base URL: http://localhost:8000
Interactive API docs (Swagger UI): ➤ http://localhost:8000/docs
Alternative documentation (ReDoc): ➤ http://localhost:8000/redoc
Health Check: ➤ http://localhost:8000/health