import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from .models import Question

# Create your tests here.

class QuestionMethodTests(TestCase):
    # methods should start with test_
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return false for questions whose
        pub_date is in the future
        :return:
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is older than 1 day
        :return:
        """
        time = timezone.now() - datetime.timedelta(days=20)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions whose
        pub_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=2)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionViewTests(TestCase):
    # If no questions exist, an appropriate message should be displayed.
    def test_index_view_with_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    # Questions with a pub_date in the past should be displayed on the index page.
    def test_index_view_with_a_past_question(self):
        q = create_question("Past question created for testing in code.", -30)
        q.choice_set.create(choice_text="choice 1", votes=22)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past question created for testing in code.>'])

    # Questions with a pub_date in the future should not be displayed on the index page.
    def test_index_view_with_a_future_question(self):
        q = create_question("Future question created for testing", 30)
        q.choice_set.create(choice_text="choice 1", votes=22)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available", status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    # Even if both past and future questions exist, only past questions should be displayed.
    def test_index_view_with_future_and_past_questions(self):
        pq = create_question("Past Question", -30)
        fq = create_question("Future Question", 30)
        pq.choice_set.create(choice_text="choice 1", votes=22)
        fq.choice_set.create(choice_text="choice 1", votes=22)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Question>'])

    def test_index_view_with_two_past_questions(self):
        p1 = create_question("Past Question 1", -30)
        p2 = create_question("Past Question 2", -5)
        p1.choice_set.create(choice_text="choice 1", votes=22)
        p2.choice_set.create(choice_text="choice 1", votes=22)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past Question 2>', '<Question: Past Question 1>'])


class QuestionIndexDetailTests(TestCase):
    # The detail view of a question with a pub_date in the future should return a 404 not found.
    def test_detail_view_with_a_future_question(self):
        future_question = create_question("Future question", 10)
        future_question.choice_set.create(choice_text="choice 1", votes=22)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        past_question = create_question("Past Question", -5)
        past_question.choice_set.create(choice_text="choice 1", votes=22)
        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)

    def test_detail_view_with_a_past_question_without_choice(self):
        past_question = create_question("Past Question", -5)
        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)

class QuestionResultsViewTests(TestCase):
    # Results view will display a 404 if future question id tried to be viewed
    def test_result_view_with_a_future_question(self):
        future_question = create_question("future question", 15)
        response = self.client.get(reverse('polls:results', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_result_view_with_a_past_question(self):
        past_question = create_question("past question", -10)
        past_question.choice_set.create(choice_text="choice 1", votes=22)
        response = self.client.get(reverse('polls:results', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)

    def test_result_view_with_no_choice_question(self):
        past_question = create_question("past question", -30)
        response = self.client.get(reverse('polls:results', args=(past_question.id,)))
        self.assertContains(response, "This question has no choices and hence cannot be viewed", status_code=200)