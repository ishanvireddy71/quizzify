import os
import json
import uuid
import random
import base64
import io
import re
import logging
from datetime import datetime

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from config import Config
from utils.scoring import ScoringEngine
from utils.validators import QuizValidator

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scoring_engine = ScoringEngine()
quiz_validator = QuizValidator()

os.makedirs(Config.DATA_DIR, exist_ok=True)
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)

def load_json(filename):
    filepath = os.path.join(Config.DATA_DIR, filename)
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filename, data):
    filepath = os.path.join(Config.DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_categories():
    data = load_json('categories.json')
    return data.get('categories', [])

def get_category(cat_id):
    cats = get_categories()
    for c in cats:
        if c.get('id') == cat_id:
            return c
    return None

def get_subcategory(cat_id, sub_id):
    cat = get_category(cat_id)
    if not cat:
        return None
    for sub in cat.get('subcategories', []):
        if sub.get('id') == sub_id:
            return sub
    return None

def get_quizzes(category=None, subcategory=None, difficulty=None):
    data = load_json('quizzes.json')
    quizzes = data.get('quizzes', [])
    if category:
        quizzes = [q for q in quizzes if q.get('category') == category]
    if subcategory:
        quizzes = [q for q in quizzes if q.get('subcategory') == subcategory]
    if difficulty:
        quizzes = [q for q in quizzes if q.get('difficulty') == difficulty]
    return quizzes

def get_quiz(quiz_id):
    quizzes = get_quizzes()
    for quiz in quizzes:
        if quiz.get('id') == quiz_id:
            return quiz
    return None

def save_quiz(quiz):
    data = load_json('quizzes.json')
    quizzes = data.get('quizzes', [])
    quizzes = [q for q in quizzes if q.get('id') != quiz.get('id')]
    quizzes.append(quiz)
    data['quizzes'] = quizzes
    save_json('quizzes.json', data)

def get_leaderboard():
    data = load_json('leaderboard.json')
    return data.get('leaderboard', [])

def get_achievements():
    data = load_json('achievements.json')
    achievements = data.get('achievements', [])
    # If no achievements exist, create defaults
    if not achievements:
        achievements = [
            {"id": "first_blood", "name": "First Blood", "description": "Complete your first quiz.", "icon": "🩸"},
            {"id": "perfect_score", "name": "Perfect Score", "description": "Get 100% on any quiz.", "icon": "💯"},
            {"id": "speed_demon", "name": "Speed Demon", "description": "Finish a quiz in under 50% of the time limit.", "icon": "⚡"},
            {"id": "streak_master", "name": "Streak Master", "description": "Answer 10 questions correctly in a row.", "icon": "🔥"},
            {"id": "category_master", "name": "Category Master", "description": "Complete at least 5 quizzes in one category.", "icon": "🏆"},
            {"id": "night_owl", "name": "Night Owl", "description": "Complete a quiz between 12 AM and 5 AM.", "icon": "🌙"},
            {"id": "quiz_creator", "name": "Quiz Creator", "description": "Create your first custom quiz.", "icon": "✏️"},
            {"id": "centurion", "name": "Centurion", "description": "Score over 1000 total points.", "icon": "🛡️"},
            {"id": "daily_warrior", "name": "Daily Warrior", "description": "Complete the daily challenge.", "icon": "📅"},
            {"id": "educator", "name": "Educator", "description": "Create a quiz from your notes.", "icon": "📚"}
        ]
        save_json('achievements.json', {'achievements': achievements})
    return achievements

def get_user_stats():
    if 'user_stats' not in session:
        session['user_stats'] = {
            'username': session.get('username', 'Guest'),
            'total_score': 0,
            'quizzes_taken': 0,
            'correct_answers': 0,
            'total_questions': 0,
            'max_streak': 0,
            'badges': [],
            'quiz_history': [],
            'quizzes_created': 0,
            'notes_quizzes': 0,
            'category_stats': {},
            'daily_completed': False,
            'last_daily': None
        }
    return session['user_stats']

def update_user_stats(result, quiz_id, category, subcategory):
    stats = get_user_stats()
    stats['total_score'] += result.get('total_score', 0)
    stats['quizzes_taken'] += 1
    stats['correct_answers'] += result.get('correct_count', 0)
    stats['total_questions'] += result.get('total_questions', 0)
    stats['max_streak'] = max(stats['max_streak'], result.get('max_streak', 0))

    cat_key = f"{category}_{subcategory}"
    if cat_key not in stats['category_stats']:
        stats['category_stats'][cat_key] = {'count': 0, 'score': 0}
    stats['category_stats'][cat_key]['count'] += 1
    stats['category_stats'][cat_key]['score'] += result.get('total_score', 0)

    stats['quiz_history'].append({
        'quiz_id': quiz_id,
        'score': result.get('total_score', 0),
        'accuracy': result.get('accuracy', 0),
        'grade': result.get('grade', 'F'),
        'date': datetime.now().isoformat(),
        'category': category,
        'subcategory': subcategory
    })

    session['user_stats'] = stats
    return stats

def generate_daily_challenge():
    all_quizzes = get_quizzes()
    if not all_quizzes:
        return None
    quiz = random.choice(all_quizzes)
    daily = dict(quiz)
    daily['id'] = 'daily_challenge'
    daily['title'] = f"Daily Challenge: {quiz['title']}"
    daily['daily'] = True
    daily['multiplier'] = Config.DAILY_CHALLENGE_MULTIPLIER
    return daily

# FIX: Better text extraction with proper error handling
def extract_text_from_pdf(filepath):
    """Extract text from PDF using multiple methods."""
    text = ""
    errors = []

    # Method 1: Try pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(filepath)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if text.strip():
            logger.info(f"pypdf extracted {len(text)} chars")
            return text, None
    except ImportError:
        errors.append("pypdf not installed")
    except Exception as e:
        errors.append(f"pypdf failed: {e}")

    # Method 2: Try PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(filepath)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if text.strip():
            logger.info(f"PyPDF2 extracted {len(text)} chars")
            return text, None
    except ImportError:
        errors.append("PyPDF2 not installed")
    except Exception as e:
        errors.append(f"PyPDF2 failed: {e}")

    # Method 3: Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            logger.info(f"pdfplumber extracted {len(text)} chars")
            return text, None
    except ImportError:
        errors.append("pdfplumber not installed")
    except Exception as e:
        errors.append(f"pdfplumber failed: {e}")

    if not text:
        return "", "PDF text extraction failed. " + "; ".join(errors) + ". The PDF may be image-based (scanned). Try converting to text first or use 'Type Notes'."
    return text, None

def extract_text_from_docx(filepath):
    """Extract text from DOCX."""
    try:
        import docx
        doc = docx.Document(filepath)
        text = '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
        if text.strip():
            return text, None
        return "", "DOCX file contains no readable text."
    except ImportError:
        return "", "python-docx not installed. Run: python -m pip install python-docx"
    except Exception as e:
        return "", f"DOCX extraction failed: {e}"

def extract_text_from_file(filepath):
    """Extract text from any supported file."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext in ('.txt', '.md', '.text'):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            if text.strip():
                return text, None
            return "", "Text file is empty."
        except Exception as e:
            return "", f"Failed to read text file: {e}"

    elif ext == '.pdf':
        return extract_text_from_pdf(filepath)

    elif ext == '.docx':
        return extract_text_from_docx(filepath)

    return "", f"Unsupported file extension: {ext}"

def extract_text_from_notes(raw_notes):
    """Extract text from notes string (handles base64 encoded files)."""
    if not raw_notes:
        return ''
    if raw_notes.startswith('__PDF_BASE64__'):
        try:
            b64 = raw_notes[len('__PDF_BASE64__'):]
            pdf_bytes = base64.b64decode(b64)
            tmp_path = os.path.join(Config.UPLOAD_DIR, f"tmp_{uuid.uuid4().hex}.pdf")
            with open(tmp_path, 'wb') as f:
                f.write(pdf_bytes)
            text, error = extract_text_from_pdf(tmp_path)
            try:
                os.remove(tmp_path)
            except:
                pass
            return text
        except Exception as e:
            logger.error(f"Base64 PDF decode failed: {e}")
            return ''
    if raw_notes.startswith('__DOCX_BASE64__'):
        try:
            b64 = raw_notes[len('__DOCX_BASE64__'):]
            docx_bytes = base64.b64decode(b64)
            tmp_path = os.path.join(Config.UPLOAD_DIR, f"tmp_{uuid.uuid4().hex}.docx")
            with open(tmp_path, 'wb') as f:
                f.write(docx_bytes)
            text, error = extract_text_from_docx(tmp_path)
            try:
                os.remove(tmp_path)
            except:
                pass
            return text
        except Exception as e:
            logger.error(f"Base64 DOCX decode failed: {e}")
            return ''
    return raw_notes

def generate_quiz_from_notes(notes_text, title, category, subcategory, difficulty='medium'):
    if not notes_text or len(notes_text.strip()) < 30:
        return None

    raw_sentences = re.split(r'(?<=[.!?])\s+', notes_text)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 30]

    questions = []
    used_words = set()

    stopwords = {'the','a','an','is','are','was','were','be','been','being',
                 'have','has','had','do','does','did','will','would','shall',
                 'should','may','might','must','can','could','of','in','on',
                 'at','by','for','with','about','as','to','and','or','but',
                 'not','from','it','its','this','that','these','those'}

    for i, sentence in enumerate(sentences[:15]):
        words = sentence.split()
        if len(words) < 6:
            continue

        candidates = [(j, w) for j, w in enumerate(words)
                      if len(w) > 4 and w.lower().rstrip('.,;:') not in stopwords
                      and w.lower() not in used_words and w[0].isalpha()]

        if not candidates:
            continue

        key_word_idx, raw_key = random.choice(candidates)
        key_word = raw_key.rstrip('.,;:')
        used_words.add(key_word.lower())

        masked = words[:]
        masked[key_word_idx] = '_____'
        question_text = f"Fill in the blank: {' '.join(masked)}"

        all_words = [w.rstrip('.,;:') for w in notes_text.split()
                     if len(w) > 4 and w[0].isalpha()
                     and w.lower().rstrip('.,;:') not in stopwords]
        distractors_pool = list({w for w in all_words if w.lower() != key_word.lower()})
        random.shuffle(distractors_pool)
        distractors = distractors_pool[:3]

        while len(distractors) < 3:
            distractors.append(f"Option {len(distractors) + 1}")

        options = distractors[:3] + [key_word]
        random.shuffle(options)
        correct_idx = options.index(key_word)

        points = {'easy': 5, 'medium': 10, 'hard': 15}.get(difficulty, 10)

        questions.append({
            'id': f'q{i+1}',
            'text': question_text,
            'options': options,
            'correct': correct_idx,
            'points': points
        })

        if len(questions) >= 10:
            break

    if len(questions) < 3:
        return None

    return {
        'id': f'notes_{uuid.uuid4().hex[:8]}',
        'title': title,
        'category': category,
        'subcategory': subcategory,
        'difficulty': difficulty,
        'time_limit': len(questions) * 60,
        'questions': questions,
        'from_notes': True
    }

@app.before_request
def init_session():
    if 'username' not in session:
        session['username'] = f"Player_{random.randint(1000, 9999)}"
    if 'theme' not in session:
        session['theme'] = 'dark'

@app.route('/')
def index():
    categories = get_categories()
    quizzes = get_quizzes()
    stats = get_user_stats()
    daily = generate_daily_challenge()
    leaderboard = get_leaderboard()[:5]

    featured = random.sample(quizzes, min(3, len(quizzes))) if quizzes else []

    return render_template('index.html',
                         categories=categories,
                         featured_quizzes=featured,
                         stats=stats,
                         daily_challenge=daily,
                         leaderboard=leaderboard,
                         theme=session.get('theme', 'dark'))

@app.route('/categories')
def categories():
    cats = get_categories()
    return render_template('categories.html', categories=cats, theme=session.get('theme', 'dark'))

@app.route('/category/<cat_id>')
def category_detail(cat_id):
    cats = get_categories()
    category = next((c for c in cats if c.get('id') == cat_id), None)
    if not category:
        return redirect(url_for('categories'))

    quizzes = get_quizzes(category=cat_id)
    stats = get_user_stats()
    cat_key_prefix = f"{cat_id}_"
    cat_quiz_count = sum(1 for k, v in stats.get('category_stats', {}).items() if k.startswith(cat_key_prefix))

    return render_template('category_detail.html',
                         category=category,
                         quizzes=quizzes,
                         cat_quiz_count=cat_quiz_count,
                         theme=session.get('theme', 'dark'))

@app.route('/subcategory/<cat_id>/<sub_id>')
def subcategory_detail(cat_id, sub_id):
    category = get_category(cat_id)
    subcategory = get_subcategory(cat_id, sub_id)
    if not category or not subcategory:
        flash('Subcategory not found', 'error')
        return redirect(url_for('categories'))
    quizzes = get_quizzes(category=cat_id, subcategory=sub_id)
    return render_template('subcategory.html',
                         category=category,
                         subcategory=subcategory,
                         quizzes=quizzes,
                         theme=session.get('theme', 'dark'))

@app.route('/quiz/<quiz_id>')
def quiz(quiz_id):
    quiz_data = get_quiz(quiz_id)
    if not quiz_data:
        if quiz_id == 'daily_challenge':
            quiz_data = generate_daily_challenge()
        if not quiz_data:
            flash('Quiz not found!', 'error')
            return redirect(url_for('index'))

    session['current_quiz'] = quiz_data
    session['current_quiz_id'] = quiz_id

    mode = request.args.get('mode', 'timed')
    return render_template('quiz.html',
                         quiz=quiz_data,
                         mode=mode,
                         theme=session.get('theme', 'dark'))

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    answers = data.get('answers', [])
    time_taken = data.get('time_taken', 0)
    mode = data.get('mode', 'timed')
    hints_used = data.get('hints_used', 0)

    quiz = session.get('current_quiz')
    if not quiz or quiz.get('id') != quiz_id:
        quiz = get_quiz(quiz_id)

    if not quiz and quiz_id == 'daily_challenge':
        quiz = generate_daily_challenge()

    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404

    result = scoring_engine.calculate_score(
        answers,
        quiz['questions'],
        time_taken,
        quiz.get('time_limit', 600),
        mode
    )

    if quiz_id == 'daily_challenge' and quiz.get('daily'):
        result['total_score'] = int(result['total_score'] * Config.DAILY_CHALLENGE_MULTIPLIER)
        result['daily_multiplier'] = Config.DAILY_CHALLENGE_MULTIPLIER

    stats = update_user_stats(result, quiz_id, quiz['category'], quiz['subcategory'])

    if quiz_id == 'daily_challenge':
        stats['daily_completed'] = True
        stats['last_daily'] = datetime.now().isoformat()

    new_badges = scoring_engine.check_achievements(result, stats)
    for badge in new_badges:
        if badge not in stats['badges']:
            stats['badges'].append(badge)

    session['user_stats'] = stats
    session['last_result'] = result
    session['last_quiz'] = quiz

    return jsonify({
        'result': result,
        'new_badges': new_badges,
        'stats': stats
    })

@app.route('/results')
def results():
    result = session.get('last_result')
    quiz = session.get('last_quiz')
    if not result:
        return redirect(url_for('index'))

    achievements = get_achievements()
    user_badges = get_user_stats().get('badges', [])

    return render_template('results.html',
                         result=result,
                         quiz=quiz,
                         achievements=achievements,
                         user_badges=user_badges,
                         theme=session.get('theme', 'dark'))

@app.route('/leaderboard')
def leaderboard():
    board = get_leaderboard()
    stats = get_user_stats()

    user_entry = {
        'rank': '-',
        'username': stats['username'],
        'total_score': stats['total_score'],
        'quizzes_taken': stats['quizzes_taken'],
        'accuracy': round((stats['correct_answers'] / stats['total_questions'] * 100), 1) if stats['total_questions'] > 0 else 0,
        'streak': stats['max_streak'],
        'badges': stats['badges']
    }

    return render_template('leaderboard.html',
                         leaderboard=board,
                         user_entry=user_entry,
                         theme=session.get('theme', 'dark'))

@app.route('/achievements')
def achievements():
    all_achievements = get_achievements()
    stats = get_user_stats()
    user_badges = stats.get('badges', [])

    for ach in all_achievements:
        ach['unlocked'] = ach['id'] in user_badges

    return render_template('achievements.html',
                         achievements=all_achievements,
                         stats=stats,
                         theme=session.get('theme', 'dark'))

@app.route('/profile')
def profile():
    stats = get_user_stats()
    all_achievements = get_achievements()
    user_badges = stats.get('badges', [])

    unlocked = [a for a in all_achievements if a['id'] in user_badges]
    locked = [a for a in all_achievements if a['id'] not in user_badges]

    return render_template('profile.html',
                         stats=stats,
                         unlocked_achievements=unlocked,
                         locked_achievements=locked,
                         theme=session.get('theme', 'dark'))

@app.route('/create')
def create_quiz():
    categories = get_categories()
    return render_template('create.html',
                         categories=categories,
                         theme=session.get('theme', 'dark'))

@app.route('/api/quiz/create', methods=['POST'])
def api_create_quiz():
    data = request.get_json()

    valid, errors = quiz_validator.validate_quiz(data)
    if not valid:
        return jsonify({'success': False, 'errors': errors}), 400

    quiz_id = f"custom_{uuid.uuid4().hex[:8]}"
    data['id'] = quiz_id
    data['created_at'] = datetime.now().isoformat()
    data['creator'] = session.get('username', 'Anonymous')

    save_quiz(data)

    stats = get_user_stats()
    stats['quizzes_created'] += 1
    if 'quiz_creator' not in stats['badges']:
        stats['badges'].append('quiz_creator')
    session['user_stats'] = stats

    return jsonify({'success': True, 'quiz_id': quiz_id})

@app.route('/create-from-notes')
def create_from_notes():
    categories = get_categories()
    return render_template('create_notes.html',
                         categories=categories,
                         theme=session.get('theme', 'dark'))

@app.route('/api/quiz/create-from-notes', methods=['POST'])
def api_create_from_notes():
    data = request.get_json()
    raw_notes = data.get('notes', '')
    title = data.get('title', 'Notes Quiz')
    category = data.get('category', 'education')
    subcategory = data.get('subcategory', 'math')
    difficulty = data.get('difficulty', 'medium')

    notes = extract_text_from_notes(raw_notes)

    valid, errors = quiz_validator.validate_notes(notes)
    if not valid:
        return jsonify({'success': False, 'errors': errors}), 400

    quiz = generate_quiz_from_notes(notes, title, category, subcategory, difficulty)
    if not quiz:
        return jsonify({'success': False, 'errors': ['Could not generate enough questions from notes. Please provide more detailed notes.']}), 400

    save_quiz(quiz)

    stats = get_user_stats()
    stats['quizzes_created'] += 1
    stats['notes_quizzes'] += 1
    if 'quiz_creator' not in stats['badges']:
        stats['badges'].append('quiz_creator')
    if 'educator' not in stats['badges']:
        stats['badges'].append('educator')
    session['user_stats'] = stats

    return jsonify({'success': True, 'quiz_id': quiz['id']})

# FIX: Completely rewritten file upload with detailed error messages
@app.route('/api/quiz/upload-file', methods=['POST'])
def api_upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'errors': ['No file uploaded']}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'errors': ['No file selected']}), 400

    allowed_extensions = {'txt', 'md', 'pdf', 'docx', 'text'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

    if ext not in allowed_extensions:
        return jsonify({'success': False, 'errors': [f'Unsupported file format: .{ext}. Use .txt, .md, .pdf, or .docx']}), 400

    filename = secure_filename(f"upload_{uuid.uuid4().hex[:8]}_{file.filename}")
    filepath = os.path.join(Config.UPLOAD_DIR, filename)

    try:
        file.save(filepath)
        logger.info(f"Saved file: {filename} ({os.path.getsize(filepath)} bytes)")
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return jsonify({'success': False, 'errors': [f'Failed to save file: {e}']}), 500

    text, error = extract_text_from_file(filepath)

    logger.info(f"Extracted {len(text) if text else 0} characters from {filename}")

    try:
        os.remove(filepath)
    except OSError:
        pass

    if error:
        return jsonify({'success': False, 'errors': [error]}), 400

    if not text or len(text.strip()) < 30:
        return jsonify({
            'success': False, 
            'errors': [f'File extracted only {len(text.strip()) if text else 0} characters. Need at least 30 characters to generate questions.']
        }), 400

    return jsonify({'success': True, 'text': text})

@app.route('/api/quiz/preview-notes', methods=['POST'])
def preview_notes_quiz():
    data = request.get_json()
    raw_notes = data.get('notes', '')
    notes = extract_text_from_notes(raw_notes)
    title = data.get('title', 'Notes Quiz')
    category = data.get('category', 'education')
    subcategory = data.get('subcategory', 'math')
    difficulty = data.get('difficulty', 'medium')

    valid, errors = quiz_validator.validate_notes(notes)
    if not valid:
        return jsonify({'success': False, 'errors': errors}), 400

    quiz = generate_quiz_from_notes(notes, title, category, subcategory, difficulty)
    if not quiz:
        return jsonify({'success': False, 'errors': ['Could not generate enough questions. Add more detailed notes.']}), 400

    return jsonify({'success': True, 'quiz': quiz})

@app.route('/api/leaderboard', methods=['GET'])
def api_leaderboard():
    board = get_leaderboard()
    return jsonify({'leaderboard': board})

@app.route('/api/categories', methods=['GET'])
def api_categories():
    cats = get_categories()
    return jsonify({'categories': cats})

@app.route('/api/quizzes', methods=['GET'])
def api_quizzes():
    category = request.args.get('category')
    subcategory = request.args.get('subcategory')
    difficulty = request.args.get('difficulty')
    quizzes = get_quizzes(category, subcategory, difficulty)
    return jsonify({'quizzes': quizzes})

@app.route('/api/stats', methods=['GET'])
def api_stats():
    return jsonify({'stats': get_user_stats()})

@app.route('/set-username', methods=['POST'])
def set_username():
    data = request.get_json()
    username = data.get('username', '').strip()
    if username and 2 <= len(username) <= 20:
        session['username'] = username
        stats = get_user_stats()
        stats['username'] = username
        session['user_stats'] = stats
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Username must be 2-20 characters'}), 400

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    current = session.get('theme', 'dark')
    session['theme'] = 'light' if current == 'dark' else 'dark'
    return jsonify({'theme': session['theme']})

@app.route('/daily-challenge')
def daily_challenge():
    daily = generate_daily_challenge()
    if not daily:
        flash('No daily challenge available today.', 'info')
        return redirect(url_for('index'))
    return redirect(url_for('quiz', quiz_id='daily_challenge'))

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)