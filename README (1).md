# Quizzify — Interactive Quiz Platform

> A modern online quiz platform with customizable quizzes, AI-powered
> question generation from study notes, real-time scoring, and a
> competitive leaderboard — built for both educational and entertainment
> use.

**🔗 [Live Demo](https://quizzify-xxx.onrender.com)** ·
**📁 [GitHub](https://github.com/YOUR_USERNAME/quizzify)**

---

## What this is

A full-stack quiz application that does what static quiz tools don't:

1. **Generate quizzes from your notes.** Paste text or upload a file
   (.txt, .pdf, .docx) and the platform automatically creates
   multiple-choice questions using NLP fill-in-the-blank generation.
2. **Two distinct categories.** Education (Mathematics, Science,
   History, Programming, etc.) and Entertainment (Gaming, Movies,
   Music, Sports, Anime, Technology).
3. **Session-consistent scoring.** Questions are stored in server-side
   sessions so the questions you answer are exactly the questions
   graded — no mismatch bugs.
4. **Achievement system.** Earn badges like "First Blood",
   "Perfect Score", "Speed Demon", and "Quiz Creator" as you play
   and create.

---

## Features

| Feature | Description |
|---------|-------------|
| 📝 Quiz from Notes | Auto-generate MCQs from pasted text or uploaded files |
| 🎨 Two Categories | Education & Entertainment with 6+ subcategories each |
| ⏱️ Timed Mode | Beat the clock with per-question time tracking |
| 🏆 Leaderboard | Global rankings updated in real-time |
| 🏅 Achievements | 10 unlockable badges based on performance |
| 🌙 Dark Theme | Purple-gradient dark UI with smooth animations |
| 📱 Responsive | Works on desktop, tablet, and mobile |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Backend | Flask 3.x, Python 3.11+ |
| Frontend | Jinja2 Templates, Vanilla CSS/JS |
| Styling | Custom dark theme with CSS animations |
| File Parsing | PyPDF2, pypdf, python-docx |
| NLP | Regex-based fill-in-the-blank generation |
| Deploy | Render (free tier) |

---

## Run Locally

Requirements: Python 3.11+, ~50MB disk for dependencies.

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/quizzify.git
cd quizzify

# 2. Create virtual environment
python -m venv .venv

# 3. Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
python app.py
```

Open http://localhost:5000.

---

## Deploy on Render

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial Quizzify commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/quizzify.git
git push -u origin main
```

### Step 2 — Deploy on Render

1. Go to [render.com](https://render.com) → Sign up with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your `quizzify` GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| Name | `quizzify` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| Plan | **Free** |

5. Click **"Create Web Service"**

Render auto-deploys on every `git push`.

---

## Repository Structure

```
quizzify/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── render.yaml               # Render deployment config
├── .env                      # Environment variables (local)
├── .gitignore                # Git ignore rules
├── data/                     # JSON data files
│   ├── categories.json       # Category/subcategory definitions
│   ├── quizzes.json          # Quiz storage
│   ├── users.json            # User profiles
│   ├── leaderboard.json      # Global rankings
│   └── achievements.json     # Badge definitions
├── templates/                # Jinja2 HTML templates
│   ├── base.html             # Base layout with navbar
│   ├── index.html            # Homepage
│   ├── categories.html       # Category listing
│   ├── category_detail.html  # Subcategory grid
│   ├── subcategory.html      # Quiz listing per subcategory
│   ├── quiz.html             # Quiz interface
│   ├── results.html          # Score breakdown
│   ├── create.html           # Manual quiz creation
│   ├── create_notes.html     # AI quiz from notes
│   ├── leaderboard.html      # Rankings
│   ├── achievements.html     # Badges
│   ├── profile.html          # User stats
│   └── login.html            # Simple auth
├── static/
│   ├── css/                  # Stylesheets
│   │   ├── main.css          # Core dark theme
│   │   ├── animations.css    # Page transitions
│   │   ├── quiz.css          # Quiz-specific styles
│   │   ├── create.css        # Creation form styles
│   │   └── leaderboard.css   # Table styles
│   └── js/                   # Client-side scripts
└── utils/
    ├── scoring.py            # Score calculation engine
    └── validators.py         # Input validation
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/categories` | GET | List all categories |
| `/api/quizzes` | GET | List quizzes (optional filters) |
| `/api/quiz/create` | POST | Create custom quiz (JSON) |
| `/api/quiz/create-from-notes` | POST | Generate quiz from notes |
| `/api/quiz/upload-file` | POST | Upload file, return extracted text |
| `/api/quiz/preview-notes` | POST | Preview questions before saving |
| `/api/quiz/submit` | POST | Submit answers, get score |
| `/api/leaderboard` | GET | Get global leaderboard |
| `/api/stats` | GET | Get current user stats |

---

## Known Limitations

- **File extraction depends on libraries.** PDF text extraction requires
  `pypdf` or `PyPDF2`; DOCX requires `python-docx`. Image-based
  (scanned) PDFs cannot be read without OCR.
- **Data is ephemeral on free tier.** Render free tier uses ephemeral
  disk; quizzes and leaderboard reset on every deploy. For production,
  migrate to PostgreSQL.
- **Session-based storage.** User stats are stored in Flask sessions;
  clearing cookies resets progress.
- **NLP is rule-based.** Question generation uses regex fill-in-the-blank,
  not LLM. Quality depends on input text structure.

---

## Future Roadmap

- [ ] PostgreSQL database for persistent storage
- [ ] User authentication (OAuth / JWT)
- [ ] LLM-powered question generation (OpenAI / Gemini)
- [ ] Multiplayer real-time quizzes (WebSockets)
- [ ] Quiz sharing via public links
- [ ] Mobile app (React Native / Flutter)

---

## License

MIT — free for personal and educational use.

---

## Author

**Your Name** — B.Tech CSE, KL University Hyderabad

GitHub: [YOUR_USERNAME](https://github.com/YOUR_USERNAME)
