class QuizValidator:
    def validate_quiz(self, data):
        errors = []
        if not data:
            return False, ['No data provided']

        if not data.get('title', '').strip():
            errors.append('Quiz title is required')
        elif len(data['title']) > 100:
            errors.append('Title must be under 100 characters')

        if not data.get('category'):
            errors.append('Category is required')
        if not data.get('subcategory'):
            errors.append('Subcategory is required')
        if data.get('difficulty') not in ['easy', 'medium', 'hard']:
            errors.append('Difficulty must be easy, medium, or hard')

        questions = data.get('questions', [])
        if len(questions) < 3:
            errors.append('At least 3 questions are required')
        elif len(questions) > 50:
            errors.append('Maximum 50 questions allowed')

        for i, q in enumerate(questions):
            q_errors = self._validate_question(q, i + 1)
            errors.extend(q_errors)

        return len(errors) == 0, errors

    def _validate_question(self, q, num):
        errors = []
        if not q.get('text', '').strip():
            errors.append(f'Question {num}: text is required')
        options = q.get('options', [])
        if len(options) < 2:
            errors.append(f'Question {num}: at least 2 options required')
        for j, opt in enumerate(options):
            if not str(opt).strip():
                errors.append(f'Question {num}, Option {j+1}: cannot be empty')
        correct = q.get('correct')
        if correct is None or not (0 <= int(correct) < len(options)):
            errors.append(f'Question {num}: correct answer index is invalid')
        return errors

    def validate_notes(self, notes):
        errors = []
        if not notes or not notes.strip():
            errors.append('Notes cannot be empty')
            return False, errors
        if len(notes.strip()) < 50:
            errors.append('Notes must be at least 50 characters long')
        sentences = [s.strip() for s in notes.split('.') if len(s.strip()) > 20]
        if len(sentences) < 3:
            errors.append('Please provide at least 3 meaningful sentences for question generation')
        return len(errors) == 0, errors