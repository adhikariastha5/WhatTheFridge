# Setup Instructions

## Quick Start

### 1. Install Prerequisites

**Install uv (Python package manager):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Install pnpm (Node.js package manager):**
```bash
npm install -g pnpm
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync

# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Run the server
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Start development server
pnpm start
```

### 4. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to `backend/.env`

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure you're in the virtual environment (`source .venv/bin/activate`)
- **Missing dependencies**: Run `uv pip install -e .` again
- **Port already in use**: Change the port in `uvicorn app.main:app --reload --port 8001`

### Frontend Issues

- **CORS errors**: Make sure the backend is running on port 8000
- **API connection failed**: Check that `http://localhost:8000` is accessible
- **Module not found**: Run `pnpm install` again

### Common Issues

- **Gemini API errors**: Verify your API key is correct and has quota remaining
- **YouTube transcript errors**: Some videos don't have transcripts available
- **Image upload fails**: Check file size (should be < 10MB) and format (JPG, PNG)

