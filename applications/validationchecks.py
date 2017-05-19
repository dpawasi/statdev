from __future__ import unicode_literals
import json

def Validation(checkname, context):
    
    if checkname == "referrals":
        donothing  = "more to come just added as a place holder"


def Attachment_Extension_Check(attach_list_type,attachments,allow_extension_types): 
    """ Purpose is to allow file extension to be checked and only allow extensions that are allowed
    """

    allowed = False 

    if allow_extension_types is None:
        allow_extension_types = ['.pdf','.xls','.doc']

    if attach_list_type == 'multi':
        """ Check a list for any attachment not meeting the allow extension list.
        """
        allowed = True
        for fi in attachments:
            att_ext = str(fi.name)[-4:].lower()
            if att_ext not in allow_extension_types:
                allowed = False

    else:
        """ By Default Assume only a single attachment
        """
        att_ext = str(attachments.name)[-4:].lower()
        if att_ext in allow_extension_types:
            allowed = True

    return allowed

