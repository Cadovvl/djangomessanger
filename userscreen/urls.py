
from django.urls import path

from userscreen.views import UserCreate, all_users, messages, send_message, main_page, user_page, my_messages, \
    user_messages

user_urls = [
    path('ym/', UserCreate.as_view()),
    path('ym/user/list/', all_users),
    path('ym/user/messages/', user_messages),
    path('ym/message/list/', messages),
    path('ym/message/send/', send_message),
    path('ym/admin_view/', main_page),
    path('ym/user/<user_id>', user_page),
    path('ym/mymessages/<user_id>', my_messages)
]

