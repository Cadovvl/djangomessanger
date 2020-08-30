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
#     # def setUp(self):
#     #     self.client = Client()
#
#     def test_messages_returns_200(self):
#         # address = reverse('messages')
#         # resp = self.client.get(address)
#         self.assertEqual(200, 200)


def refresh(message: models.Message) -> None:
    message.refresh_from_db(using=1)


def wait_and_return_list(arg):
    time.sleep(0.05)
    return []

class TestMessages(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_dummy(self):
        self.assertEqual(1, 1)

    def test_refresh(self):
        message = mock.Mock(spec=models.Message)
        refresh(message)
        message.refresh_from_db.assert_called_with(using=1)

    @mock.patch('userscreen.models.User.objects', mock.Mock())
    def test_all_users(self):
        models.User.objects.all = mock.Mock()
        models.User.objects.all.return_value = []
        self.client.get(reverse('all_users'))
        models.User.objects.all.assert_called_with()


    @mock.patch('userscreen.models.Message.objects', mock.Mock())
    def message_cached(self):
        models.Message.objects.\
            select_related.return_value.\
            order_by.return_value = []

        self.client.get(reverse('messages'))
        self.client.get(reverse('messages'))
        self.client.get(reverse('messages'))
        self.client.get(reverse('messages'))
        self.client.get(reverse('messages'))
        self.client.get(reverse('messages'))

        self.assertEqual(1, models.Message.objects.select_related.call_count)

    @mock.patch('userscreen.models.Message.objects', mock.Mock())
    def parallel_message_cached(self):
        models.Message.objects.\
            select_related.return_value.\
            order_by.side_effect = wait_and_return_list

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

    #
    # @mock.patch('userscreen.models.Message.objects', mock.Mock())
    # def message_error_cached(self):
    #     models.Message.objects.\
    #         select_related.return_value.\
    #         order_by.side_effect = KeyError('asd')
    #
    #     self.client.get(reverse('messages'))
    #     self.client.get(reverse('messages'))
    #     self.client.get(reverse('messages'))
    #     self.client.get(reverse('messages'))
    #     self.client.get(reverse('messages'))
    #     self.client.get(reverse('messages'))
    #
    #     self.assertEqual(1, models.Message.objects.select_related.call_count)

    def test_message_cached(self):
        self.message_cached()
        time.sleep(0.5)
        self.parallel_message_cached()
        # time.sleep(0.5)
        # self.message_error_cached()
