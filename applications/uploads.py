from django.http import HttpResponse
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.conf import settings
from django.core.exceptions import ValidationError
from ledger.accounts.models import EmailUser
from applications.models import Referral
from confy import env
from .models import Record
import json
from django.utils.safestring import SafeText
"""
This is a upload wrapper for the ajax uploader widget for django forms.
"""

def ApplicationUploads(request):
    #  print request.FILES
    object_hash = {} 
 #   print request.FILES
#    print request.POST
    for f in request.FILES.getlist('files'):
    #for f in request.FILES.getlist('__files[]'):
         doc = Record()
         doc.upload = f
         doc.name = f.name
         doc.save()
#         self.object.records.add(doc)
#         print doc.id
         object_hash['doc_id'] = doc.id
         object_hash['path'] = doc.upload.name
         object_hash['short_name'] = SafeText(doc.upload.name)[19:]
         object_hash['name'] = doc.name
        
         doc2 = Record.objects.get(id=object_hash['doc_id'])
         # print doc
    json_hash = json.dumps(object_hash)
    return HttpResponse(json_hash, content_type='text/html')
