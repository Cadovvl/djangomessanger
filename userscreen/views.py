from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import CreateView

from userscreen.models import User, Message


class UserCreate(CreateView):
    model = User
    template_name = 'create_user.html'
    fields = ['nickname', 'realname']
    success_url = '/user/list/'



def all_users(request):
    users = User.objects.all()
    return render(request, 'users.html', { 'users': [u for u in users]})


def messages(request):
    messages = Message.objects.order_by('-id')[:30]
    formatted = [f"{ m.author.nickname} :  { m.text }" for m in messages]
    return render(request, 'messages.html', {'messages':  formatted})


def send_message(request):
    print(request.POST)
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
