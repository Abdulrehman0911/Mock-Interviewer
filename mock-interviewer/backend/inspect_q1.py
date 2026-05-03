import json
from pathlib import Path

f = Path('data/questionsAnswers.json')
data = json.load(open(f))
q_list = data.get('Software Engineer', [])

# Find Q1
for q in q_list:
    if q['question_id'] == 1:
        print(f"Q{q['question_id']}: {q['question']}")
        print("\nAnswers:")
        for i, ans in enumerate(q['answers']):
            print(f"\n  Answer {i+1} (quality={ans.get('quality_score')}):")
            print(f"    Text: {ans.get('text', '')[:100]}...")
            print(f"    Keywords: {ans.get('keywords', [])[:10]}")
        break
