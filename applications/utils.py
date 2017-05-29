from __future__ import unicode_literals
from django.db.models import Q
import random
import re
import string


def random_dpaw_email():
    """Return a random email address ending in dpaw.wa.gov.au
    """
    s = ''.join(random.choice(string.ascii_letters) for i in range(20))
    return '{}@dpaw.wa.gov.au'.format(s)


def get_query(query_string, search_fields):
    """Function to return a Q object that can be used to filter a queryset.
    A search string and a list of model fields is passed in.

    Splits the query string into individual keywords, getting rid of extra
    spaces and grouping quoted words together as a phrase (use double quotes).
    """
    findterms = re.compile(r'"([^"]+)"|(\S+)').findall
    normspace = re.compile(r'\s{2,}').sub
    query = None  # Query to search for every search term
    terms = [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query
