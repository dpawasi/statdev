from django.conf import settings
from django.contrib.auth.models import Group 

def has_group(user):
    staff_groups = ['Approver','Assessor','Director','Emergency','Executive','Processor']
    user_groups = user.groups.all()
    for sg in user_groups:
        group = Group.objects.get(name=sg)
        if group in user.groups.all():
            return True
    return False

def has_staff(user):
    if user.is_staff is True:
        return True
    else:
        return False

def has_admin(user):
    staff_groups = ['Processor']
    user_groups = user.groups.all()
    for sg in user_groups:
        group = Group.objects.get(name=sg)
        if group in user.groups.all():
            return True
    return False

def template_context(request):
    """Pass extra context variables to every template.
    """
    context = {
        'project_version': settings.APPLICATION_VERSION_NO,
        'project_last_commit_date': settings.GIT_COMMIT_DATE,
        'staff': has_staff(request.user),
        'admin_staff': has_admin(request.user)
        #['Approver','Assessor','Director','Emergency','Executive','Processor']
    }
    return context


