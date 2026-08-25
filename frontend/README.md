# Intelligent Land Record Digitization and Validation System

This project is an AI-powered system that digitizes scanned historical land records, extracts structured information using OCR/AI, validates the extracted information, and allows a government officer to review and approve the records.

This repository contains both the React frontend and the Python FastAPI backend.

---

## 1. Local Development Setup

### Prerequisites
- **Node.js** (v18 or higher)
- **Python** (v3.10 or higher)
- **Git**

### Backend Setup

1. Open a terminal and navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic python-multipart pydantic-settings
   ```

4. Start the development server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   > The backend API will now be available at `http://localhost:8000`.

### Frontend Setup

1. Open a **new** terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install the Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   > The frontend application will now be available at `http://localhost:5173`.

---

## 2. Vercel & Production Deployment Guide

Since this is a full-stack application (React frontend + Python FastAPI backend), you should deploy them to their respective environments. Vercel is highly recommended for the React frontend, while the FastAPI backend should be deployed to a service like Render or Railway.

### Step 1: Deploy Backend (e.g., to Render or Railway)
1. Push your code to a GitHub repository.
2. Go to [Render](https://render.com/) or [Railway](https://railway.app/) and create a new "Web Service".
3. Connect your GitHub repository and set the root directory to `backend`.
4. Set the Start Command to: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Once deployed, note down your backend's public URL (e.g., `https://my-land-api.onrender.com`).

### Step 2: Configure Frontend for Vercel
Before deploying the frontend, tell it where the live backend is located.

1. Go to your `frontend` directory.
2. The codebase uses `import.meta.env.VITE_API_BASE_URL` for API calls.

### Step 3: Deploy Frontend to Vercel
1. Go to [Vercel](https://vercel.com/) and create a new project.
2. Connect your GitHub repository.
3. In the Vercel project setup screen:
   - **Framework Preset**: Vercel will automatically detect `Vite`.
   - **Root Directory**: Click "Edit" and select the `frontend` folder.
   - **Environment Variables**: Add a new variable named `VITE_API_BASE_URL` and set its value to your live backend URL (e.g., `https://my-land-api.onrender.com`).
4. Click **Deploy**.

> **Note for Vercel React Router:**
> To prevent "Page Not Found" errors when refreshing routes on Vercel, ensure you have a `vercel.json` file in the root of your `frontend` directory:
> ```json
> {
>   "rewrites": [
>     { "source": "/(.*)", "destination": "/index.html" }
>   ]
> }
> ```
