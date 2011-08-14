from django.conf import settings
from django.core.cache import cache

# max lenght of the history list.
VISITHISTORY_MAX_LENGTH = getattr(settings, 'VISITHISTORY_MAX_LENGTH', 5)

# default cache timeout. Cache entries can get lost even before this value!
VISITHISTORY_TIMEOUT = getattr(settings, 'VISITHISTORY_TIMEOUT', 30000)


class VisitHistory(object):
    """
    VisitHistory saves a list of visited pages/objects, and a allows to return
    these later on. It used djangos Caching framework to save this list, so
    it can be get lost at any time. On the positive side, it is very fast.

    Use it only if you have a centraliced caching system when you use multiple
    webserver, or the list will appear / change / get lost everytime another
    cache server is asked.

    The system takes objects that contain a method "get_absolute_url" as content,
    and returns a special list of VisitHistoryEntry instances later on.
    For speed reasons, it saves the get_absolute_url on add-time, also the
    content of unicode(object).
    """

    user = None
    key = ''

    def __init__(self, user):
        """
        Every list is for an own user, so this is a must-have parameter
        """
        self.user = user
        self.key = self.__buildkey(user)

    def add(self, object, additional_data = {}):
        """
        Adds a new object to the history list. You can save addition information
        alongside the default unicode() and get_absolute_url (+ the object)
        values. This can be usefull to show the list later on without the need
        to do any more database requests.

        If the list is already at VISITHISTORY_MAX_LENGTH length, the oldest entry
        will be dropped.

        VISITHISTORY_TIMEOUT is used
        """

        # we use our own get() function, but without limit, to prevent any
        # problems here with changed VISITHISTORY_MAX_LENGTH values
        list = self.get(False)

        # used to init a new list
        if not list:
            list = []

        list.insert(0, VisitHistoryEntry(
                url = object.get_absolute_url(),
                object = object,
                additional_data = additional_data,
            ))

        # drop the oldest entries if the list is longer then allowed
        if len(list) > VISITHISTORY_MAX_LENGTH:
            list = list[0:VISITHISTORY_MAX_LENGTH]

        cache.set(self.key, list, VISITHISTORY_TIMEOUT)

    def get(self, limit = VISITHISTORY_MAX_LENGTH, object_class = False):
        """
        get() can be used to load retrieve the saved history entries, in a whole
        (default limit or False) or with a specific limit value. Also the list
        can be filteres by class (only usefull with classed that are added
        at some time to the history...).

        Example:

          result = history.get(5)  <- last 5 entries

          result = history.get(5, TestModel)  <- last 5 entries for class TestModel

          result = history.get()  <- Last VISITHISTORY_MAX_LENGTH entries (normally all)
          result = history.get(False)  <- Absolutly all entries, ignoring VISITHISTORY_MAX_LENGTH

        Important: Since old entries are deleted in add(), ignoring VISITHISTORY_MAX_LENGTH
        is normally not usefull
        """

        list = cache.get(self.key)

        # used to return a valid list if cached didn't return one
        if not list:
            return []

        # when object_class filter is set, we test every single object in the
        # list if it fits. This is done BEFORE limit is used. So we
        # limit on all entries of a class found later.
        if object_class:
            new_list = []
            for entry in list:
                if isinstance(entry.object, object_class):
                    new_list.append(entry)
            list = new_list

        # limit is optional, if False if given, all data are returned
        if limit:
            return list[0:limit]
        else:
            return list

    def __buildkey(self, user):
        return 'VisitHistory:' + str(user.id)


class VisitHistoryEntry(object):
    """
    Helper class to save the objects given to VisitHistory.
    It saves not only the object itself, but also the content of "unicode(object)"
    and the result of object.get_absolute_url().
    Both is done to use these data later on without the need to
    """

    url = None
    text = None
    object = None
    additional_data = {}

    def __init__(self, url, object, additional_data = {}):
        self.url = url
        self.text = unicode(object)
        self.object = object
        self.additional_data = additional_data