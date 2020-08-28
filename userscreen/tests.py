from django.test import Client, TestCase
import unittest
import mock
import time
import threading

from userscreen import models

# Create your tests here.
from django.urls import reverse

#
# class TestMessages(TestCase):
#
#     def setUp(self):
#         self.client = Client()
#
#     def test_messages_returns_200(self):
#         address = reverse('messages')
#         resp = self.client.get(address)
#         self.assertEqual(resp.status_code, 200)


def refresh(mess: models.Message) -> None:
    mess.refresh_from_db()


def wait_and_return_empty_list(arg):
    time.sleep(0.05)
    return []


class TestMessagesCache(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_mocking(self):
        message = mock.Mock(spec=models.Message)
        refresh(message)
        message.refresh_from_db.assert_called_with()

    @mock.patch('userscreen.models.User.objects', mock.Mock())
    def test_all_users(self):
        models.User.objects.all = mock.Mock(return_value=[])
        self.client.get(reverse('all_users'))
        models.User.objects.all.assert_called_with()

    @mock.patch('userscreen.models.Message.objects', mock.Mock())
    def messages_cached(self):
        models.Message.objects.\
            select_related.return_value.\
            order_by.return_value = []

        self.client.get(reverse('messages'))
        self.client.get(reverse('messages'))
        self.client.get(reverse('messages'))
        self.client.get(reverse('messages'))
        self.client.get(reverse('messages'))

        self.assertEqual(1, models.Message.objects.select_related.call_count)


    @mock.patch('userscreen.models.Message.objects', mock.Mock())
    def async_messages_cached(self):
        models.Message.objects.\
            select_related.return_value.\
            order_by.side_effect = wait_and_return_empty_list

        a1 = threading.Thread(target=lambda: self.client.get(reverse('messages')))
        a2 = threading.Thread(target=lambda: self.client.get(reverse('messages')))
        a3 = threading.Thread(target=lambda: self.client.get(reverse('messages')))

        a1.start()
        a2.start()
        a3.start()

        a1.join()
        a2.join()
        a3.join()

        self.assertEqual(1, models.Message.objects.select_related.call_count)



    # @mock.patch('userscreen.models.Message.objects', mock.Mock())
    # def messages_cached_with_error(self):
    #     models.Message.objects.\
    #         select_related.return_value.\
    #         order_by.side_effect = KeyError('any error')
    #
    #     self.client.get(reverse('messages'))
    #     self.client.get(reverse('messages'))
    #     self.client.get(reverse('messages'))
    #     models.Message.objects. \
    #         select_related.return_value. \
    #         order_by.return_value = []
    #
    #     self.client.get(reverse('messages'))
    #     self.client.get(reverse('messages'))
    #
    #     self.assertEqual(3, models.Message.objects.select_related.call_count)
    #


    def test_messages(self):
        self.messages_cached()
        time.sleep(1.0)
        self.async_messages_cached()
        # time.sleep(1.0)
        # self.messages_cached_with_error()


