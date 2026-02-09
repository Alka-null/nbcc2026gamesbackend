from django.db import migrations

def create_sample_questions(apps, schema_editor):
    Question = apps.get_model('gameplay', 'Question')
    sample_data = [
        {'text': 'What is the capital of France?', 'correct_answer': 'Paris'},
        {'text': 'What is 2 + 2?', 'correct_answer': '4'},
        {'text': 'What color is the sky?', 'correct_answer': 'Blue'},
        {'text': 'Who wrote Hamlet?', 'correct_answer': 'Shakespeare'},
        {'text': 'What is the boiling point of water?', 'correct_answer': '100'},
    ]
    for q in sample_data:
        Question.objects.create(**q)

class Migration(migrations.Migration):
    dependencies = [
        ('gameplay', '0002_question_quizstat'),
    ]
    operations = [
        migrations.RunPython(create_sample_questions),
    ]
