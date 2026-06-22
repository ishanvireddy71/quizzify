from datetime import datetime


class ScoringEngine:

    def calculate_score(self, answers, questions, time_taken, time_limit, mode='timed'):
        n = len(questions)
        padded = list(answers) + [{"selected": None}] * n
        padded = padded[:n]

        correct_count = 0
        total_points = 0
        max_streak = 0
        current_streak = 0
        answers_detail = []

        for i, (q, ans) in enumerate(zip(questions, padded)):
            if isinstance(ans, dict):
                selected = ans.get('selected')
            elif isinstance(ans, int):
                selected = ans
            else:
                selected = None

            correct_idx = q.get('correct', -1)
            q_points = q.get('points', 10)
            q_text = q.get('text', 'Question ' + str(i + 1))
            q_options = q.get('options', [])

            is_correct = (selected is not None) and (int(selected) == int(correct_idx))

            if is_correct:
                correct_count += 1
                total_points += q_points
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0

            answers_detail.append({
                'question_index': i,
                'question_text': q_text,
                'options': q_options,
                'selected': selected,
                'correct': correct_idx,
                'selected_option': selected,
                'correct_option': correct_idx,
                'is_correct': is_correct,
                'points': q_points if is_correct else 0
            })

        accuracy = round((correct_count / n) * 100, 1) if n > 0 else 0
        base_score = total_points

        time_bonus = 0
        streak_bonus = 0
        perfect = correct_count == n and n > 0

        if mode == 'timed' and time_taken < time_limit:
            time_ratio = 1 - (time_taken / time_limit)
            time_bonus = int(base_score * 0.3 * time_ratio)

        if max_streak >= 3:
            streak_bonus = int(base_score * 0.1 * (max_streak // 3))

        total_score = base_score + time_bonus + streak_bonus

        grade = self._calculate_grade(accuracy)

        return {
            'total_score': total_score,
            'base_score': base_score,
            'base_points': base_score,
            'time_bonus': time_bonus,
            'streak_bonus': streak_bonus,
            'accuracy_bonus': 0,
            'correct_count': correct_count,
            'total_questions': n,
            'accuracy': accuracy,
            'max_streak': max_streak,
            'time_taken': time_taken,
            'grade': grade,
            'perfect': perfect,
            'answers_detail': answers_detail,
            'time_limit': time_limit
        }

    def _calculate_grade(self, accuracy):
        if accuracy == 100:
            return 'S'
        elif accuracy >= 90:
            return 'A+'
        elif accuracy >= 80:
            return 'A'
        elif accuracy >= 70:
            return 'B'
        elif accuracy >= 60:
            return 'C'
        elif accuracy >= 50:
            return 'D'
        else:
            return 'F'

    def check_achievements(self, result, stats):
        new_badges = []
        existing = set(stats.get('badges', []))

        checks = [
            ('first_blood',    stats.get('quizzes_taken', 0) >= 1),
            ('perfect_score',  result.get('perfect', False)),
            ('speed_demon',    result.get('time_taken', 999) < (result.get('time_limit', 600) * 0.5)
                               if 'time_limit' in result else False),
            ('streak_master',  result.get('max_streak', 0) >= 10),
            ('centurion',      stats.get('total_score', 0) >= 1000),
        ]

        hour = datetime.now().hour
        if 0 <= hour < 5:
            checks.append(('night_owl', True))

        cat_stats = stats.get('category_stats', {})
        for cat_key, cat_data in cat_stats.items():
            if cat_data.get('count', 0) >= 5:
                checks.append(('category_master', True))
                break

        for badge_id, condition in checks:
            if condition and badge_id not in existing:
                new_badges.append(badge_id)

        return new_badges