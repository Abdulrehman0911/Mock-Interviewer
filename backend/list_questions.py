import json
from pathlib import Path

f = Path('data/questionsAnswers.json')
data = json.load(open(f))
q_list = data.get('Software Engineer', [])

for q in q_list[:12]:
    print(f"Q{q['question_id']}: {q['question'][:70]}")
