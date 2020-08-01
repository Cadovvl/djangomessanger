
from django.urls import path

from userscreen.views import UserCreate, all_users, messages, send_message, main_page, user_page

user_urls = [
    path('user/create/', UserCreate.as_view()),
    path('user/list/', all_users),
    path('message/list/', messages),
    path('message/send/', send_message),
    path('', main_page),
    path('user/<user_id>', user_page)
]

