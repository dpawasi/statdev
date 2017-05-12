from __future__ import unicode_literals
from applications.workflow import Flow
from .models import Location, Document, PublicationNewspaper, PublicationWebsite, PublicationFeedback,Referral,Application
from django.utils.safestring import SafeText
from django.contrib.auth.models import Group

class Application_Part5():

    def get(self,app,self_view,context):
        request = self_view.request
      
        if app.routeid is None:
            app.routeid = 1

        flow = Flow()
        flow.get('part5')
        context = flow.getAccessRights(request,context,app.routeid,'part5')
        context = flow.getCollapse(context,app.routeid,'part5')
        context = flow.getHiddenAreas(context,app.routeid,'part5')
        context['workflow_actions'] = flow.getAllRouteActions(app.routeid,'part5')
        context['formcomponent'] = flow.getFormComponent(app.routeid,'part5')
        try:
              LocObj = Location.objects.get(application_id=self_view.object.id)
              context['certificate_of_title_volume'] = LocObj.title_volume
              context['folio'] = LocObj.folio
              context['diagram_plan_deposit_number'] = LocObj.dpd_number
              context['location'] = LocObj.location
              context['reserve_number'] = LocObj.reserve
              context['street_number_and_name'] = LocObj.street_number_name
              context['town_suburb'] = LocObj.suburb
              context['lot'] = LocObj.lot
              context['nearest_road_intersection'] = LocObj.intersection
        except:
              donothing = ''

        context['publication_newspaper'] = PublicationNewspaper.objects.filter(application_id=self_view.object)
        context['publication_website'] = PublicationWebsite.objects.filter(application_id=self_view.object)
        if self_view.object.river_lease_scan_of_application:
            context['river_lease_scan_of_application_short'] = SafeText(self_view.object.river_lease_scan_of_application.upload.name)[19:]

        if self_view.object.document_draft:
            context['document_draft_short'] = SafeText(self_view.object.document_draft.upload.name)[19:]
        if self_view.object.document_final:
            context['document_final_short'] = SafeText(self_view.object.document_final.upload.name)[19:]
        if self_view.object.deed:
            context['deed_short'] = SafeText(self_view.object.deed.upload.name)[19:]

     
        context['land_owner_consent_list'] = []
        landoc = app.land_owner_consent.all()
        for doc in landoc:
            fileitem = {}
            fileitem['fileid'] = doc.id
            fileitem['path'] = doc.upload.name
            fileitem['path_short'] = SafeText(doc.upload.name)[19:]
            context['land_owner_consent_list'].append(fileitem)


        context['publication_newspaper_list'] = []
        pub_news_obj = []
        pub_news_mod  = PublicationNewspaper.objects.filter(application_id=self_view.object)
        for pubrow in pub_news_mod:
            rowitem = {}
            rowitem['pk'] = pubrow.pk
            rowitem['id'] = pubrow.id
            rowitem['date'] = pubrow.date
            rowitem['newspaper'] = pubrow.newspaper
            rowitem['application'] = pubrow.application
            rowitem['documents'] = pubrow.documents
            rowitem['documents_short'] = []
            documents = pubrow.documents.all()
            for doc in documents:
                fileitem = {}
                fileitem['fileid'] = doc.id
                fileitem['path'] = doc.upload
                fileitem['path_short'] = SafeText(doc.upload.name)[19:]
                rowitem['documents_short'].append(fileitem)
            context['publication_newspaper_list'].append(rowitem)


        pub_feed_obj = []
        pub_feed_mod = PublicationFeedback.objects.filter(application_id=self_view.object)
        for pubrow in pub_feed_mod:
            rowitem = {}
            rowitem['id'] = pubrow.id
            rowitem['name'] = pubrow.name
            rowitem['address'] = pubrow.address
            rowitem['suburb'] = pubrow.suburb
            rowitem['state'] = pubrow.state
            rowitem['postcode'] = pubrow.postcode
            rowitem['phone'] = pubrow.phone
            rowitem['email'] = pubrow.email
            rowitem['comments'] = pubrow.comments
            rowitem['documents'] = pubrow.documents
            rowitem['documents_short'] = [] # needed so we can add documents to list
            rowitem['status'] = pubrow.status
            rowitem['application'] = pubrow.application
            documents = pubrow.documents.all()
            for doc in documents:
                fileitem = {}
                fileitem['fileid'] = doc.id
                fileitem['path'] = doc.upload
                fileitem['path_short'] = SafeText(doc.upload.name)[19:]
                rowitem['documents_short'].append(fileitem)
            pub_feed_obj.append(rowitem)

        context['publication_feedback'] = pub_feed_obj
      
        new_documents_to_publish = {}
        pub_web = PublicationWebsite.objects.filter(application_id=self_view.object.id)
        for pub_doc in pub_web:
            if pub_doc.published_document_id:
                doc = Document.objects.get(id=pub_doc.published_document_id)
                fileitem = {}
                fileitem['fileid'] = doc.id
                fileitem['path'] = doc.upload.name
                new_documents_to_publish[pub_doc.original_document_id] = fileitem

        orignaldoclist = []
        if self_view.object.river_lease_scan_of_application:
            fileitem = {}
            fileitem['fileid'] = self_view.object.river_lease_scan_of_application.id
            fileitem['path'] = self_view.object.river_lease_scan_of_application.upload.name
            fileitem['path_short'] = SafeText(self_view.object.river_lease_scan_of_application.upload.name)[19:]
            fileitem['group_name'] = "River Lease Scan of Application"
            if self_view.object.river_lease_scan_of_application.id in new_documents_to_publish:
                fileitem['publish_doc'] = new_documents_to_publish[self_view.object.river_lease_scan_of_application.id]['path']
                fileitem['publish_doc_short'] = SafeText(new_documents_to_publish[self_view.object.river_lease_scan_of_application.id]['path'])[19:]
            orignaldoclist.append(fileitem)

        if self_view.object.deed:
             fileitem = {}
             fileitem['fileid'] = self_view.object.deed.id
             fileitem['path'] = self_view.object.deed.upload.name
             fileitem['path_short'] = SafeText(self_view.object.deed.upload.name)[19:]
             fileitem['group_name'] = "Deed"
             if self_view.object.deed.id in new_documents_to_publish:
                 fileitem['publish_doc'] = new_documents_to_publish[self_view.object.deed.id]['path']
                 fileitem['publish_doc_short'] = SafeText(new_documents_to_publish[self_view.object.deed.id]['path'])[19:]
             orignaldoclist.append(fileitem)

        landoc = app.land_owner_consent.all()
        for doc in landoc:
            fileitem = {}
            fileitem['fileid'] = doc.id
            fileitem['path'] = doc.upload.name
            fileitem['path_short'] = SafeText(doc.upload.name)[19:]
            fileitem['group_name'] = "Land Owner Consent"
            if doc.id in new_documents_to_publish:
                fileitem['publish_doc'] = new_documents_to_publish[doc.id]['path']
                fileitem['publish_doc_short'] = SafeText(new_documents_to_publish[doc.id]['path'])[19:]
            else:
                fileitem['publish_doc'] = ""
                fileitem['publish_doc_short'] = ""

            orignaldoclist.append(fileitem)

        doclist = app.proposed_development_plans.all()
        for doc in doclist:
            fileitem = {}
            fileitem['fileid'] = doc.id
            fileitem['path'] = doc.upload.name
            fileitem['path_short'] = SafeText(doc.upload.name)[19:]
            fileitem['group_name'] = "Proposed Development Plans"

            if doc.id in new_documents_to_publish:
                fileitem['publish_doc'] = new_documents_to_publish[doc.id]['path']
                fileitem['publish_doc_short'] = SafeText(new_documents_to_publish[doc.id]['path'])[19:]
            else:
                fileitem['publish_doc'] = ""
                fileitem['publish_doc_short'] = ""
            orignaldoclist.append(fileitem)
        context['original_document_list'] = orignaldoclist

        doclist = app.proposed_development_plans.all()
        context['proposed_development_plans_list'] = []
        for doc in doclist:
            fileitem = {}
            fileitem['fileid'] = doc.id
            fileitem['path'] = doc.upload.name
            fileitem['path_short'] = SafeText(doc.upload.name)[19:]
            context['proposed_development_plans_list'].append(fileitem)

        return context


class Application_Emergency():

    def get(self,app,self_view,context):
        request = self_view.request
        workflowtype = "emergency"

        if app.routeid is None:
            app.routeid = 1

        flow = Flow()
        flow.get(workflowtype)
        context = flow.getAccessRights(request,context,app.routeid,workflowtype)
        context = flow.getCollapse(context,app.routeid,workflowtype)
        context = flow.getHiddenAreas(context,app.routeid,workflowtype)
        context['workflow_actions'] = flow.getAllRouteActions(app.routeid,workflowtype)
        context['formcomponent'] = flow.getFormComponent(app.routeid,workflowtype)

        if app.organisation:
           context['address'] = app.organisation.postal_address
        elif app.applicant:
           context['address'] = app.applicant.emailuserprofile.postal_address

        return context

class Application_Permit():
    def get(self,app,self_view,context):
        request = self_view.request
        workflowtype = "permit"

        if app.routeid is None:
            app.routeid = 1

        flow = Flow()
        flow.get(workflowtype)
        context = flow.getAccessRights(request,context,app.routeid,workflowtype)
        context = flow.getCollapse(context,app.routeid,workflowtype)
        context = flow.getHiddenAreas(context,app.routeid,workflowtype)
        context['workflow_actions'] = flow.getAllRouteActions(app.routeid,workflowtype)
        context['formcomponent'] = flow.getFormComponent(app.routeid,workflowtype)

        return context
        
class Application_Licence():
    def get(self,app,self_view,context):
        request = self_view.request
        workflowtype = "licence"

        if app.routeid is None:
            app.routeid = 1

        flow = Flow()
        flow.get(workflowtype)
        context = flow.getAccessRights(request,context,app.routeid,workflowtype)
        context = flow.getCollapse(context,app.routeid,workflowtype)
        context = flow.getHiddenAreas(context,app.routeid,workflowtype)
        context['workflow_actions'] = flow.getAllRouteActions(app.routeid,workflowtype)
        context['formcomponent'] = flow.getFormComponent(app.routeid,workflowtype)
        return context


class Referrals_Next_Action_Check():

    def get(self,app):
        app_refs = Referral.objects.filter(application=app)
#       print app_refs
        referralscompleted = True
        for ref in app_refs:
            if ref.status == Referral.REFERRAL_STATUS_CHOICES.referred:
                referralscompleted = False
            
        return referralscompleted

    def go_next_action(self,app):
        app = Application.objects.get(id=app.id)
        app.status = ''
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        DefaultGroups = flow.groupList()
        flow.get(workflowtype)
        assignee = None
        routes = flow.getAllRouteActions(app.routeid,workflowtype)
        action = routes[0]['routegroup']
        if action in DefaultGroups['grouplink']:
            groupassignment = Group.objects.get(name=DefaultGroups['grouplink'][action])
        else:
            groupassignment = None
        route = flow.getNextRouteObj(action,app.routeid,workflowtype)

        if "route"in route:
            app.routeid = route["route"]
        else: 
            app.routeid = None

        if "state" in route:
            app.state = route["state"]
        else:
            app.state = None

        app.group = groupassignment
        app.assignee = assignee
        app.save()
 



