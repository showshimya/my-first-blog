from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice
# Create your views here.
# making change to push changes

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        # return Question.objects.order_by('-pub_date')[:5]
        # making it print only the published date is till today
        questions_list = Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:10]
        display_list = []
        for question in questions_list:
            if question.choice_set.count() != 0:
                display_list.append(question)
        return display_list

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        # Exclude any questions that are not published
        question_published = Question.objects.filter(pub_date__lte=timezone.now())
        return question_published


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        question_published = Question.objects.filter(pub_date__lte=timezone.now()).filter(choice_set.count()__!=0)
        return question_published


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:4]
    # output = ','.join([p.question_text for p in latest_question_list])
    # return HttpResponse(output)
    # one way to display using templates
    # template = loader.get_template('polls/index.html')
    # context = RequestContext(request, {'latest_question_list': latest_question_list})
    # return HttpResponse(template.render(context))
    # other way to display using render and its easy
    return render(request, 'polls/index.html', {'latest_question_list': latest_question_list})


def detail(request, question_id):
    # try:
    #    question = Question.objects.get(pk=question_id)
    # except Question.DoesNotExist:
    #    raise Http404("Question does not exist")
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})
    # return HttpResponse("You are looking at question %s." % question_id)


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


def vote(request, question_id):
    q = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = q.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # redisplay the question voting form
        return render(request, 'polls/detail.html', {
            'question': q,
            'error_message': "You did not select a choice."
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing with POST data.
        # This prevents data from being posted twice of user hits the back button
        return HttpResponseRedirect(reverse('polls:results', args=(q.id,)))
