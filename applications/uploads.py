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
from applications.validationchecks import Attachment_Extension_Check, is_json
"""
This is a upload wrapper for the ajax uploader widget for django forms.
"""

def ApplicationUploads(request):
    #  print request.FILES
    object_hash = {'status':'success','message':''} 
 #   print request.FILES
#    print request.POST
    allow_extension_types = ['.pdf','.xls','.doc','.jpg','.png','.xlsx','.docx','.msg']

    for f in request.FILES.getlist('files'):
         extension = f.name.split('.')
         att_ext = str("."+extension[1]).lower()
         if att_ext not in allow_extension_types:
             object_hash['status'] = 'error'
             object_hash['message'] = 'Extension not allowed'+str(att_ext)
                 
             json_hash = json.dumps(object_hash)
             return HttpResponse(json_hash, content_type='text/html')

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
