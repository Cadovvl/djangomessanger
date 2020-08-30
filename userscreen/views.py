from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import CreateView

from userscreen.models import User, Message
import functools
import time
from django.db import connection, reset_queries

class UserCreate(CreateView):
    model = User
    template_name = 'create_user.html'
    fields = ['nickname', 'realname']
    success_url = '/user/list/'

def debug_query(func):
    def inner_func(*arc, **argv):

        print(f"Starting: {func.__name__}")
        reset_queries()
        sq = len(connection.queries)

        start = time.perf_counter()
        result = func(*arc, **argv)
        end = time.perf_counter()

        eq = len(connection.queries)

        print(f"Finish: {func.__name__}")
        print(f"Finished for : {end - start:.2f}s")
        print(f"Total {eq - sq} queries")

        for i in connection.queries:
            print(i)

        return result

    return inner_func


def cached(func):
    last_val = None
    last_modified = 0.0

    @functools.wraps(func)
    def inner_func(request):
        nonlocal last_val
        nonlocal last_modified
        if time.time() - last_modified > 0.5:
            last_modified = time.time()
            last_val = func(request)
            last_modified = time.time()
        return last_val

    return inner_func


def all_users(request):
    users = User.objects.all()
    return render(request, 'users.html', { 'users': [u for u in users]})


# @cached
def messages(request):
    messages = Message.objects.select_related('author').order_by('-id')[:30]
    formatted = reversed([f"{ m.author.nickname} :  { m.text }" for m in messages])
    return render(request, 'messages.html', {'messages':  formatted})


def send_message(request):
    if 'message' not in request.POST\
            or 'author' not in request.POST:
        return HttpResponse("message and author is required", status=400) # bad request

    message_text = request.POST['message']

    # todo: author type validation!!!
    message = Message(text=message_text, author_id=int(request.POST['author']))
    message.save()
    return HttpResponse(f'Id: {message.id}', status=201) # created


def main_page(request):
    mm = Message.objects.order_by('-id')[:30]
    formatted = reversed([f"{ m.author.nickname} :  { m.text }" for m in mm])

    me = User.objects.get(id=1)
    my_messages = me.messages.order_by("-id")[:20]

    return render(request, 'main_page.html',
                  {'messages':  formatted,
                   'users': User.objects.all(),
                   "user": me,
                   "my_messages": my_messages
                   })


def user_page(request, user_id):
    mm = Message.objects.order_by('-id')[:30]
    formatted = reversed([f"{ m.author.nickname} :  { m.text }" for m in mm])

    me = User.objects.get(id=user_id)
    my_messages = me.messages.order_by("-id")[:20]

    return render(request, 'user_page.html',
                  {'messages':  formatted,
                   'users': User.objects.all(),
                   "user": me,
                   "my_messages": my_messages,
                   'user_id': user_id
                   })


def my_messages(request, user_id):
    me = User.objects.get(id=user_id)
    my_messages = me.messages.order_by("-id")[:20]

    return render(request, 'messages.html',
                {
                  'messages': [m.text for m in my_messages]
                })
@cached
def user_messages(request):
    users = User.objects.prefetch_related(
        Prefetch(
            lookup='messages',
            queryset=Message.objects.order_by("-id"),
            to_attr='ordered_messages'
        )
    ).all()[:10]
    messages = [{'name': u.nickname, 'messages': u.ordered_messages[:10] } for u in users]

    return render(request, 'user_messages.html',
    {
        'users': messages
    })
