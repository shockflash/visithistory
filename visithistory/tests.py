# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache

from models import VisitHistory, VISITHISTORY_MAX_LENGTH

class TestModel(object):
    id = ''

    def __init__(self, id):
        self.id = str(id)

    def get_absolute_url(self):
        return 'url ' + self.id

class TestModelSecond(object): # used in get(object_class = ...)
    def get_absolute_url(self):
        return '....'



class VisitHistoryTests(TestCase):

    def setUp(self):
        self.user = User()
        self.user.save()
        self.v = VisitHistory(self.user)

    def test_simple_set_get(self):
        v = VisitHistory(self.user)

        testm1 = TestModel('1')
        self.v.add(testm1)

        testm2 = TestModel('2')
        self.v.add(testm2)

        result = self.v.get()

        self.assertEqual(result[0].url, 'url 2')
        self.assertEqual(result[1].url, 'url 1')

    def test_listmax(self):
        """ Test that the VISITHISTORY_MAX_LENGTH is used.
            Since the value is dynamic, we test it dynamic. We try to add more
            values then allowed, and test if the keeped entries are the last
            ones added """
        v = VisitHistory(self.user)

        testedMax = 0
        for i in range(1, VISITHISTORY_MAX_LENGTH + 17): # 17 is "random"
            test = TestModel(i)
            self.v.add(test)
            testedMax = i

        result = self.v.get(1000) # 1000 to ensure that the get limit won't affect the test
        self.assertEqual(len(result), VISITHISTORY_MAX_LENGTH)

        pos = testedMax
        for entry in result:
            self.assertEqual(entry.url, 'url ' + str(pos))
            pos = pos - 1

    def test_get_limit(self):
        """ Test of tje get parameter "limit" works, and that it works without it """
        v = VisitHistory(self.user)

        testedMax = 0
        for i in range(1, VISITHISTORY_MAX_LENGTH + 1):
            test = TestModel(i)
            self.v.add(test)
            testedMax = i

        result = self.v.get()
        self.assertEqual(len(result), VISITHISTORY_MAX_LENGTH)

        result = self.v.get(2)
        self.assertEqual(len(result), 2)

    def test_get_class(self):
        """ test class filtering """

        v = VisitHistory(self.user)

        test = TestModel(1)
        self.v.add(test)

        result = self.v.get()
        self.assertEqual(len(result), 1)

        result = self.v.get(object_class = TestModel)
        self.assertEqual(len(result), 1)

        result = self.v.get(object_class = TestModelSecond)
        self.assertEqual(len(result), 0)

        # now test if get(limit...) works
        for i in range(3):
            test = TestModelSecond()
            self.v.add(test)

        test = TestModel('x')
        self.v.add(test)

        result = self.v.get(object_class = TestModelSecond)
        self.assertEqual(len(result), 3)

        result = self.v.get(2, object_class = TestModelSecond)
        self.assertEqual(len(result), 2)

        # result must not only be limited, but all results must have the right
        # object class
        self.assertTrue(isinstance(result[0].object, TestModelSecond))
        self.assertTrue(isinstance(result[1].object, TestModelSecond))

    def test_multi_users(self):
        """ Test that no object added to one user is visible for another user"""

        self.user2 = User()
        self.user2.username = 'seconduser'
        self.user2.save()

        # test for first user
        test = TestModel('1')
        self.v.add(test)
        result = self.v.get()
        self.assertEqual(result[0].url, 'url 1')

        # test for second user
        v2 = VisitHistory(self.user2)
        test = TestModel('A')
        v2.add(test)
        result = v2.get()
        self.assertEqual(result[0].url, 'url A')

        # another test for first user. Entries for second user should not show up
        v3 = VisitHistory(self.user)
        test = TestModel('2')
        v3.add(test)
        result = v3.get()
        self.assertEqual(result[0].url, 'url 2')
        self.assertEqual(result[1].url, 'url 1')