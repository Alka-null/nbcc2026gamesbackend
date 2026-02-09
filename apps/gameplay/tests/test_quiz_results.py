from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class QuizResultApiTests(APITestCase):
    def test_guest_can_submit_quiz_score(self):
        url = reverse('quiz-results-list')
        payload = {'player_name': 'Guest Player', 'score': 8, 'total_questions': 10}

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('leaderboard', response.data)
        self.assertGreaterEqual(len(response.data['leaderboard']), 1)
        self.assertEqual(response.data['leaderboard'][0]['score'], 8)
