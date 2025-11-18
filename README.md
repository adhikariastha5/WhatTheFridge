# WhatTheFridge 🍳

An AI-powered cooking assistant that helps you find recipes based on available ingredients, powered by LangGraph, Gemini AI, and React.

## Features

- **Ingredient Input**: Enter ingredients via text or upload an image
- **Recipe Discovery**: Search recipes from YouTube and web sources
- **Video Transcription**: Automatically extract step-by-step instructions from YouTube videos
- **AI Chat Assistant**: Customize recipes, adjust serving sizes, and adapt to available cooking equipment using Gemini AI
- **Smart Recipe Suggestions**: Get personalized recipe recommendations based on your ingredients and cravings

## Tech Stack

### Backend
- **FastAPI**: REST API framework
- **LangGraph**: Agent workflow orchestration
- **Google Gemini**: LLM for chat and vision
- **OpenCV**: Image preprocessing
- **YouTube APIs**: Video search and transcript extraction
- **Web Scraping**: Recipe extraction from blogs

### Frontend
- **React**: UI framework
- **Axios**: HTTP client

### Package Managers
- **uv**: Fast Python package manager
- **pnpm**: Fast Node.js package manager

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- uv (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- pnpm (install: `npm install -g pnpm`)
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create a virtual environment and install dependencies with uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

3. Create a `.env` file:
```bash
cp .env.example .env
```

4. Add your Gemini API key to `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

5. Run the backend server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies with pnpm:
```bash
pnpm install
```

3. Start the development server:
```bash
pnpm start
```

The app will open at `http://localhost:3000`

## Usage

1. **Enter Ingredients**: Type in your available ingredients or upload an image
2. **Add Craving** (optional): Specify what you're in the mood for
3. **Get Recipes**: Browse suggested recipes from YouTube and web sources
4. **View Steps**: Click to see step-by-step cooking instructions
5. **Chat with AI**: Ask the assistant to customize recipes, adjust serving sizes, or adapt to your cooking equipment

## API Endpoints

- `POST /api/ingredients` - Submit ingredients and get recipe suggestions
- `POST /api/chat` - Chat with the cooking assistant
- `GET /api/recipes?conversation_id={id}` - Get recipes for a conversation
- `GET /api/transcribe/{video_id}` - Get YouTube video transcript

## Project Structure

```
WhatTheFridge/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph agent workflow
│   │   ├── models/         # Pydantic schemas
│   │   ├── services/       # External service integrations
│   │   └── main.py         # FastAPI application
│   └── pyproject.toml      # Python dependencies (uv)
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   └── App.jsx         # Main app component
│   └── package.json        # Node dependencies (pnpm)
└── README.md
```

## Future Enhancements

- Physical cooking robot integration (Raspberry Pi/Jetson Nano)
- Voice command support
- Automated grocery ordering
- Real-time cooking assistance
- Multi-language support

## License

MIT
