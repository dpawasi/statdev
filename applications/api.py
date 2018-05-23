from django.http import HttpResponse
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.conf import settings
from django.core.exceptions import ValidationError
from confy import env
import json
from django.utils.safestring import SafeText
from django.utils.crypto import get_random_string
import os
from . import models
from django.core import serializers
import collections
import datetime
"""
This is a upload wrapper for the ajax uploader widget for django forms.
"""

def getPredefinedCondition(request,precond_id):
    if request.user.is_staff:
       object_hash = models.ConditionPredefined.objects.get(id=precond_id,status=1)
       json_hash = serializers.serialize('json', [object_hash])
       #listing = buildListingArray(object_hash)
       #json_hash = json.dumps(object_hash)
    else:
       json_hash = json.dumps({"error":"Access Denied"})

    return HttpResponse(json_hash, content_type='text/html')


