# Hospital Management System App v2

A role-based web application that enables admins, doctors, and patients to manage hospital data, appointments, and treatments efficiently.

## Installation

### Node.js
1. Install Node.js 20 (LTS)
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt install -y nodejs
   ```
2. Verify installation
   ```bash
   node -v
   npm -v
   ```

### Redis
1. Install Redis
   ```bash
   sudo apt update
   sudo apt install redis-server
   ```
2. Start the Redis Server
   ```bash
   sudo systemctl start redis-server
   ```
3. Check if the server is reachable
   ```bash
   redis-cli ping
   ```

## Steps to set up and run the app locally (on linux)

### Clone the repository
   ```bash
   git clone https://github.com/23f3000826/hospital-management-app.git
   ```

### Set up Backend Environment
1. Navigate to the backend folder:
   ```bash
   cd /path/to/hospital-management-app/backend
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```
3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
4. Install the Python dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Create a .env file and add the following
   ```bash
   APP_SECRET=your_app_secret

   MAIL_USERNAME=yourname@gmail.com
   MAIL_PASSWORD=your_google_app_password
   
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/1
   CELERY_RESULT_BACKEND=redis://localhost:6379/2
   ```

### Set up Celery
1. Open a new terminal
2. Navigate to the backend folder:
   ```bash
   cd /path/to/hospital-management-app/backend
   ```
3. Start Celery Worker:
   ```bash
   celery -A celery_app.celery_app worker --loglevel=info
   ```
4. Open another new terminal
5. Navigate to the backend folder:
   ```bash
   cd /path/to/hospital-management-app/backend
   ```
6. Start Celery Beat:
   ```bash
   celery -A celery_app.celery_app beat --loglevel=info
   ```

### Start the Flask Server
1. Open a new terminal
2. Navigate to the backend folder:
   ```bash
   cd /path/to/hospital-management-app/backend
   ```
3. Run the app:
   ```bash
   python3 app.py
   ```

### Start the Vite Server
1. Open a new terminal
2. Navigate to the frontend folder:
   ```bash
   cd /path/to/hospital-management-app/frontend
   ```
3. Install the dependencies:
   ```bash
   npm install
   ```
4. Start the server:
   ```bash
   npm run dev
   ```
5. Open `localhost:5173` in your browser

## Clean up
1. Stop the Vite server, Flask server, Celery Worker, Celery Beat using `Ctrl + C` in the terminal where they are open.
2. Stop the Redis server:
   ```bash
   sudo systemctl stop redis-server
   ```
3. Navigate to the backend folder:
   ```bash
   cd /path/to/hospital-management-app/backend
   ```
4. Deactivate the virtual environment:
   ```bash
   deactivate
   ```

Hospital Icon Image Credit: mehedi.dce/Vecteezy