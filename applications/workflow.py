from __future__ import unicode_literals
from django.contrib.auth.models import Group
import json
__all__ = (
        "Flow"
)

class Flow():
    def get(self,flow):
        with open('applications/flowconf/workflow.'+flow+'.json') as json_data_file:
            json_obj = json.load(json_data_file)
        return json_obj
#       print(data['1']['groupaccess']['Processor'])
#       print(data['1']['title'])
#       print data
    def getAllRouteConf(self,flow,routeid):
        with open('applications/flowconf/workflow.'+flow+'.json') as json_data_file:
            json_obj = json.load(json_data_file)
            if routeid:
                if json_obj[str(routeid)]:
                    return json_obj[str(routeid)]
            return None
    def getGroupAccess(self,context,route,group,flow): 
        if "may_update" not in context:
            context["may_update"] = "False"
        if "may_lodge" not in context:
            context["may_lodge"] = "False"
        if "may_refer" not in context:
            context["may_refer"] = "False"
        if "may_assign_customer" not in context:
            context["may_assign_customer"] = "False"
        if "may_assign_processor" not in context:
            context["may_assign_processor"] = "False"
        if "may_assign_assessor" not in context:
            context["may_assign_assessor"] = "False"
        if "may_request_compliance" not in context:
            context["may_request_compliance"] = "False"
        if "may_assign" not in context:
            context["may_assign"] = "False"
        if "may_create_condition" not in context:
            context["may_create_condition"] = "False"
        if "may_submit_approval" not in context:
            context["may_submit_approval"] = "False"
       	if "may_issue" not in context:
            context["may_issue"] = "False"
        if "may_generate_pdf" not in context:
            context["may_generate_pdf"] = "False"


        with open('applications/flowconf/workflow.'+flow+'.json') as json_data_file:
            json_obj = json.load(json_data_file)
            if json_obj[str(route)]:
                if "groupaccess" in json_obj[str(route)]:
                    if json_obj[str(route)]['groupaccess'][group]:
                        groupaccess = json_obj[str(route)]['groupaccess'][group]
                        for ga in groupaccess:
                            if ga in context:
                                if context[ga]:
                                    if context[ga] in 'True':
                                        donothing = ''            
                                    else:
                                      context[ga] = groupaccess[ga]
                            else:
                                context[ga] = groupaccess[ga]
        return context
    def getAllGroupAccess(self,request,context,route,flow):
        processor = Group.objects.get(name='Processor')
        assessor = Group.objects.get(name='Assessor')
        approver = Group.objects.get(name='Approver')
        referee = Group.objects.get(name='Referee')
 
        if processor in request.user.groups.all():
            context = self.getGroupAccess(context,route,'Processor',flow)
        if assessor in request.user.groups.all():
            context = self.getGroupAccess(context,route,'Assessor',flow)
        if approver in request.user.groups.all():
            context = self.getGroupAccess(context,route,'Approver',flow)
        if referee in request.user.groups.all():
            context = self.getGroupAccess(context,route,'Referee',flow)

        return context
    def getCollapse(self,context,route,flow):
        context['collapse'] = {} 
        with open('applications/flowconf/workflow.'+flow+'.json') as json_data_file:
            json_obj = json.load(json_data_file)
            if "collapse" in json_obj[str(route)]: 
                collapse = json_obj[str(route)]['collapse']
                for c in collapse:
                    if collapse[c] in "False":
                       context['collapse'][c] = "in"
        return context

    def getHiddenAreas(self,context,route,flow):
        context['hidden'] = {}
        with open('applications/flowconf/workflow.'+flow+'.json') as json_data_file:
           json_obj = json.load(json_data_file)
           if json_obj[str(route)]:
               if json_obj[str(route)]['hidden']:
                  context["hidden"] = json_obj[str(route)]['hidden']
        return context
    def getFields(self,context,route,flow):
        context['fields'] = {}
        with open('applications/flowconf/workflow.'+flow+'.json') as json_data_file:
           json_obj = json.load(json_data_file)
           if json_obj[str(route)]:
               if json_obj[str(route)]['fields']:
                  context["fields"] = json_obj[str(route)]['fields']
        return context
    def getNextRoute(self,action,route,flow):
        with open('applications/flowconf/workflow.'+flow+'.json') as json_data_file:
            json_obj = json.load(json_data_file)
            if json_obj[str(route)]:
                if json_obj[str(route)]['actions']:
                    for a in json_obj[str(route)]['actions']:
                        if a["routegroup"]:
                            if a["routegroup"] == action:
                               return a["route"]





