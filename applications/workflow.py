from __future__ import unicode_literals
import json

class Flow():
    def get(self,flow):
        with open('applications/config/workflow.'+flow+'.json') as json_data_file:
            json_obj = json.load(json_data_file)
        return json_obj
#       print(data['1']['groupaccess']['Processor'])
#       print(data['1']['title'])
#       print data 
    def getGroupAccess(self,context,route,group,flow): 
        with open('applications/config/workflow.'+flow+'.json') as json_data_file:
            json_obj = json.load(json_data_file)
            groupaccess = json_obj['1']['groupaccess']['Processor']
            for ga in groupaccess:
                #                print ga
                if ga in context:
                    if context[ga]:
                        if context[ga] in 'True':
                            donothing = ''            
                        else:
                          context[ga] = groupaccess[ga]
                else:
                    context[ga] = groupaccess[ga]
#            print groupaccess
        return context
    def getCollapse(self,context,route,flow):
        context['collapse'] = {} 
        with open('applications/config/workflow.'+flow+'.json') as json_data_file:
            json_obj = json.load(json_data_file)
            
            collapse = json_obj['1']['collapse']
            for c in collapse:
                if collapse[c] in "False":
                    context['collapse'][c] = "in"
        return context




