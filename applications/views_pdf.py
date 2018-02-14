# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Location, Record, PublicationNewspaper, PublicationWebsite, PublicationFeedback,Referral,Application, Delegate, Compliance
from django.utils.safestring import SafeText
from django.contrib.auth.models import Group
from django.db.models import Q
from applications.email import sendHtmlEmail, emailGroup, emailApplicationReferrals
from fpdf import FPDF
import textwrap

class PDFtool():

    bullet_number_count = int(1)
    def create_para(self,pdf,text):

        para_split =  textwrap.wrap(text, 116)
        for p in para_split:
            pdf.cell(0, 5, p ,0,1,'L')
        return pdf

    def horizontal_line(self,pdf):
#        pdf.line(7, 110, 205, 110)
        current_font_family = pdf.font_family
        current_font_size = pdf.font_size_pt
        current_font_style = pdf.font_style
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 1,'_____________________________________________________________' ,0,1,'L')
        pdf.cell(0, 4, ' ' ,0,1,'L')
        pdf.set_font(current_font_family,current_font_style,current_font_size)
        return pdf
    def heading1_bold(self,pdf,text):
        current_font_family = pdf.font_family
        current_font_size = pdf.font_size_pt
        current_font_style = pdf.font_style
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 7, text,0,1,'L')
        pdf.set_font(current_font_family,current_font_style,current_font_size)
        return pdf

    def heading2_bold(self,pdf,text):
        current_font_family = pdf.font_family
        current_font_size = pdf.font_size_pt
        current_font_style = pdf.font_style
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, text,0,1,'L')
        pdf.set_font(current_font_family,current_font_style,current_font_size)
        return pdf

    def column_para(self,pdf,column1,column2,column1width):
        if column1width is None:
           column1width = 80
        loop = 1
        para_split =  textwrap.wrap(column2, 118 - column1width)
        for p in para_split:
 
            if loop > 1:
                pdf.cell(6, 5, ' ',0,0,'L')
                pdf.cell(column1width, 5, ' ' ,0,0,'L')
                pdf.cell(6, 5, ':',0,0,'L')
                pdf.cell(6, 5, p ,0,1,'L')
            else:
                pdf.cell(6, 5, ' ',0,0,'L')
                pdf.cell(column1width, 5, column1 ,0,0,'L')
                pdf.cell(6, 5, ':',0,0,'L')
                pdf.cell(6, 5, p ,0,1,'L')
            loop = loop + 1

        return pdf

    def column_para_no_seperator(self,pdf,column1,column2,column1width,indent):
        if column1width is None:
           column1width = 80
        if indent is None:
           indent = 1
        loop = 1
        para_split =  textwrap.wrap(column2, 118 - column1width)
        for p in para_split:

            indentloop = 0
            while indentloop < indent:
                pdf.cell(6, 5, ' ',0,0,'L')
                indentloop = indentloop + 1

            if loop > 1:
                indentloop = 0
                
#                pdf.cell(6, 5, ' ',0,0,'L')
                pdf.cell(column1width, 5, ' ' ,0,0,'L')
                pdf.cell(6, 5, p ,0,1,'L')
            else:
 #               pdf.cell(6, 5, ' ',0,0,'L')
                pdf.cell(column1width, 5, column1 ,0,0,'L')
                pdf.cell(6, 5, p ,0,1,'L')
            loop = loop + 1

    
#        pdf.cell(6, 5, ' ',0,0,'L')
 #       pdf.cell(column1width, 5, column1 ,0,0,'L')
  #      pdf.cell(6, 5, column2 ,0,1,'L')
        return pdf


    def column_para_bold(self,pdf,column1,column2,column1width):
        if column1width is None:
           column1width = 80
        current_font_family = pdf.font_family
        current_font_size = pdf.font_size_pt
        current_font_style = pdf.font_style
 
        loop = 1
        para_split =  textwrap.wrap(column2, 118 - column1width)
        for p in para_split:
            
            if loop > 1:
                pdf.set_font('Arial', 'B', current_font_size)
                pdf.cell(6, 5, ' ',0,0,'L')
                pdf.cell(column1width, 5, ' ' ,0,0,'L')
                pdf.set_font(current_font_family,'I',current_font_size)
                pdf.cell(6, 5, p ,0,1,'L')
            else: 
                pdf.set_font('Arial', 'B', current_font_size)
                pdf.cell(6, 5, ' ',0,0,'L')
                pdf.cell(column1width, 5, column1 ,0,0,'L')
                pdf.set_font(current_font_family,'I',current_font_size)
                pdf.cell(6, 5, p ,0,1,'L')
            loop = loop + 1

        pdf.set_font(current_font_family,current_font_style,current_font_size)

        return pdf


    def bullet_numbers_para(self,pdf,text):
        loop = 1
        pdf.cell(0,5,' ', 0,1,'L')

        para_split =  textwrap.wrap(text, 110)
        for p in para_split:
            if loop > 1:
                pdf.cell(10, 5, ' ',0,0,'L')
                pdf.cell(60, 5, p ,0,1,'L')
            else:
                pdf.cell(10, 5, str(self.bullet_number_count)+'.',0,0,'L')
                pdf.cell(60, 5, p ,0,1,'L')
            loop = loop + 1

        self.bullet_number_count = self.bullet_number_count + 1
        return pdf

    def pre_text_bold_para(self,pdf,boldtext,normaltext):
        pdf.cell(0,5,' ', 0,1,'L')

    def space(self,pdf):
        pdf.cell(0,5,' ', 0,1,'L')
        return pdf
    def generate_licence(self):
         pdf = FPDF('P', 'mm', 'A4')
         pdf.add_page()
         # pdf.image('plugins/flightsensation/images/flight_voucher.jpg', 0, 0, 210,297)

         #swan_canning_riverpark_dbca.png
         pdf.image('applications/static/images/swan_canning_riverpark_dbca.png', 30, 7, 144,24)

         pdf.set_font('Arial', 'I', 10)
         pdf.cell(0,28,' ', 0,1,'L')

         pdf = self.create_para(pdf,'Pursuant to Section 32 of the Swan and Canning Rivers Management Act 2006 and Part 4 (Regulation 29) of the Swan and Canning Rivers Management Regulations 2007, this is to certify that a licence and permit are issued to the person(s) or organisation described hereunder as licence and permit holder and that person(s) or organisation is permitted to carry out the authorised acts or activities for the duration specified subject to the conditions listed below.')
 #        pdf.set_font('Arial', 'B', 16)
         #print pdf.font_family
          #rint pdf.font_size_pt
         #print pdf.font_size_pt

        # from pprint import pprint
#         pprint(vars(pdf))
  #       pdf.cell(0, 1,'_____________________________________________________________' ,0,1,'L')

         pdf.set_font('Arial', '', 10)
         pdf = self.horizontal_line(pdf)
         pdf = self.column_para(pdf,'Licence/Permit holder','',None)
         # group spacer
         pdf = self.space(pdf)
         pdf = self.column_para(pdf,'Authorised works, acts or activities:','',None)
         pdf = self.space(pdf)
         pdf = self.column_para(pdf,'Location of works, acts or activities:','',None)
         pdf = self.space(pdf)
         pdf = self.column_para(pdf,'Vessel details:','',None)
         pdf = self.space(pdf)
         pdf = self.column_para(pdf,'Approval date:','',None)
         pdf = self.space(pdf)
         pdf = self.column_para(pdf,'Expiry date:','',None)
         pdf = self.horizontal_line(pdf)

         pdf = self.heading1_bold(pdf,'PERMIT LICENCE XXXXX')
         pdf = self.heading2_bold(pdf,'CONDITION(S)')
         pdf = self.bullet_numbers_para(pdf,'Whilst operating within the Swan Canning Riverpark, a copy of this approval shall remain with this operation at all times, and must be shown to a government inspector on demand.')
         pdf = self.bullet_numbers_para(pdf,'The Operator shall abide by the Specific Licence Conditions and General Licence Conditions of Licence LXXXXX (refer below).')
         pdf = self.bullet_numbers_para(pdf,'The Operator does not have priority access over other users to any area of the Swan Canning Development Control Area.')
         pdf = self.bullet_numbers_para(pdf,'The Operator shall not erect any structures (including signage) or store any equipment associated with the operation within the Swan Canning Development Control Area.')
         pdf = self.bullet_numbers_para(pdf,'The Operator shall ensure that no damage to the riverbed, foreshore or vegetation within the Swan Canning Development Control Area occurs as a result of the Operation.  The Operator shall make good any damage to the river and/or foreshore area, to the satisfaction of the Department.')
         pdf = self.bullet_numbers_para(pdf,'The Operator shall ensure that no damage to the riverbed, foreshore or vegetation within the Swan Canning Development Control Area occurs as a result of the Operation.  The Operator shall make good any damage to the river and/or foreshore area, to the satisfaction of the Department.')
         pdf = self.bullet_numbers_para(pdf,'Refuelling within the River reserve shall be undertaken at a licensed refuelling facility and by a person with a coxswain\'s certificate, or higher maritime qualification.')
         pdf = self.bullet_numbers_para(pdf,'The Operator shall ensure that no sewage, greywater, fuel, garbage or other solid or liquid waste material enters the River reserve as a result of the operation.')
         pdf = self.bullet_numbers_para(pdf,'The Operator shall have sullage tanks installed and operational in the vessel.')
         pdf = self.bullet_numbers_para(pdf,'General waste and refuse generated aboard the vessel must not be disposed of by use of public bins installed at jetties, parks or other locations, including commercial bins at East Street Jetty and Barrack Street Jetty (unless by prior arrangement with the relevant authority).')
         pdf = self.bullet_numbers_para(pdf,'The Operator\'s vessel shall not anchor in any area that may cause restrictions to navigating traffic or secure the Operator\'s vessel to any mooring buoy that is not lawful to use.')
         pdf = self.bullet_numbers_para(pdf,'The Operator shall not create undue noise or nuisance through its Operations.')
         pdf = self.bullet_numbers_para(pdf,'The Operator\'s vessel shall not enter any gazetted marine park within the Swan River without lawful authority pursuant to the Conservation and Land Management Regulations 2002 from the Department.')
         pdf = self.bullet_numbers_para(pdf,'The Operator shall not transit through the Narrows Personal Watercraft Area.')
         pdf = self.bullet_numbers_para(pdf,'The Operator shall obtain all relevant approvals from other government authorities (e.g. relevant local government authorities, and Department of Transport) that may be required, including the permission to berth at any public jetties, and if requested by the Department, supply copies of such approvals to the Director of the Rivers and Estuaries Division.')

         pdf = self.create_para(pdf,'<<Other conditions to follow here>>')
         pdf = self.create_para(pdf,'<<Advice to Applicant>>')
         pdf = self.heading2_bold(pdf,'DEFINITIONS')
     
         pdf = self.column_para_bold(pdf,'Act','means the Swan and Canning Rivers Management Act 2006.',30)
         pdf = self.column_para_bold(pdf,'Department','means the Department of Biodiversity, Conservation and Attractions.',30)
         pdf = self.column_para_bold(pdf,'Director General','means the chief executive officer (CEO) of the Department (the department assisting the Minister in the administration of the Act) or a delegate of the CEO.',30)
         pdf = self.column_para_bold(pdf,'Operations','means the commercial operations which may be undertaken by an operator pursuant to the licence.',30)
         pdf = self.column_para_bold(pdf,'Operator','means a person (includes incorporated bodies) who holds a licence.',30)
         pdf = self.column_para_bold(pdf,'Regulations', 'means the Swan and Canning Rivers Management Regulations 2007.',30)
         pdf = self.column_para_bold(pdf,'River reserve', 'means the reserve over the Swan and Canning rivers defined in section 11(2) and described in Schedule 4 of the Act.',30)


         pdf = self.heading2_bold(pdf,'INTERPRETATION')
         pdf = self.column_para_no_seperator(pdf,'a.', 'A reference to anything that the Operator must or must not do includes, where the context permits, the Operator\'s employees, agents, and contractors.',10,1)
         pdf = self.space(pdf)
         pdf = self.column_para_no_seperator(pdf,'b.', 'The singular includes the plural and vice versa.',10,1)
         pdf = self.space(pdf)

         pdf = self.column_para_no_seperator(pdf,'c.', 'A reference to any thing is a reference to the whole or any part of it and a reference to a group of things or persons is a reference to any one or more of them.',10,1)
         pdf = self.space(pdf)

         pdf = self.column_para_no_seperator(pdf,'d.', 'If the Operator consists of a partnership or joint venture, then:',10,1)
         pdf = self.space(pdf)

         pdf = self.column_para_no_seperator(pdf,'i.', 'an obligation imposed on the Operator binds each person who comprises the Operator jointly and severally;',10,3)
         pdf = self.space(pdf)



         pdf = self.column_para_no_seperator(pdf,'e.', 'A reference to a statute, ordinance, code or other law includes regulations and other instruments under it and consolidations, amendments, re-enactments or replacements of any of them',10,1)
         pdf = self.space(pdf)




         pdf = self.column_para_no_seperator(pdf,'f.', 'If a word or phrase is defined, other grammatical forms of that word or phrase have a corresponding meaning.',10,1)
         pdf = self.space(pdf)

         pdf = self.column_para_no_seperator(pdf,'g.', 'If the word "including" or "includes" is used, the words "without limitation" are taken to immediately follow.',10,1)
         pdf = self.space(pdf)





         pdf = self.bullet_numbers_para(pdf,'')
         pdf = self.bullet_numbers_para(pdf,'')
         pdf = self.bullet_numbers_para(pdf,'')
         pdf = self.bullet_numbers_para(pdf,'')



         #pdf.cell(0, 5, 'Pursuant to Part 4 (Regulation 29) of the Swan and Canning Rivers Management Regulations 2007, this',0,1,'L')
         #pdf.cell(0, 5, 'is to certify that a permit is issued to the person(s) or organisation described hereunder as permit holder',0,1,'L')
         #pdf.cell(0, 5, 'and that person(s) or organisation is permitted to carry out the authorised works, acts or activities for',0,1,'L')
         #pdf.cell(0, 5, 'duration specified, subject to the conditions listed below.',0,1,'L')



         pdf.cell(0,33,' ', 0,1,'L')
         pdf.cell(0, 8, 'Swan and Canning Rivers Management Act 2006',0,1,'C')
         pdf.set_font('Arial', 'B', 10)
         pdf.cell(0, 8, 'SECTION 84',0,1,'C')
         pdf.set_font('Arial', 'BU', 10)
         pdf.cell(0, 8, 'DETERMINATION OF REQUEST FOR VARIATION',0,1,'C')
         pdf.set_font('Arial', '', 9)


         pdf.output('pdfs/approvals/4-approval.pdf', 'F')


    def generate_section_84(self):

         pdf = FPDF('P', 'mm', 'A4')
         pdf.add_page()
         # pdf.image('plugins/flightsensation/images/flight_voucher.jpg', 0, 0, 210,297)

         #swan_canning_riverpark_dbca.png
         pdf.image('applications/static/images/swan_canning_riverpark_dbca.png', 30, 7, 144,24)

         pdf.set_font('Arial', 'I', 10)
         pdf.cell(0,33,' ', 0,1,'L')
         pdf.cell(0, 8, 'Swan and Canning Rivers Management Act 2006',0,1,'C')
         pdf.set_font('Arial', 'B', 10)
         pdf.cell(0, 8, 'SECTION 84',0,1,'C')
         pdf.set_font('Arial', 'BU', 10)
         pdf.cell(0, 8, 'DETERMINATION OF REQUEST FOR VARIATION',0,1,'C')
         pdf.set_font('Arial', '', 9)

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         #pdf.cell(6, 5, ' ',0,0,'L')
         #pdf.cell(60, 5, 'FILE NUMBER',0,0,'L')
         #pdf.cell(6, 5, ':',0,0,'L')
         #pdf.cell(6, 5, '1100',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'APPROVAL NUMBER',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, '',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'APPLICANT',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, '21 cars st kensington',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'APPLICANT\'S ADDRESS',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, '21 cars st kensington',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'LANDOWNER',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, '',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'LAND DESCRIPTION',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, '',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'DEVELOPMENT',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, '',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'DESCRIPTION OF CHANGES',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, '',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'SECTION 84 DETERMINATION',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, '',0,1,'L')

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.set_font('Arial', 'B', 10)
         pdf.cell(60, 5, 'DETERMINATION',0,1,'L')
         pdf.set_font('Arial', '', 9)

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'In accordance with Section 84(1)(a) of the Swan and Canning Rivers Management Act 2006, I hereby:',0,1,'L')

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, '1.',0,0,'L')
         pdf.cell(60, 5, 'Authorise the minor variations to Development Approval [approval number] to allow for [title of section 84].',0,1,'L')

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, '2.',0,0,'L')
         pdf.cell(60, 5, 'Grant this Section 84 approval subject to compliance with all the following conditions and advice notes. All',0,1,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, '  ',0,0,'L')
         pdf.cell(60, 5, 'conditions and advice notes shall apply and remain in force for the duration of the approval period.',0,1,'L')

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.set_font('Arial', 'B', 10)
         pdf.cell(60, 5, 'CONDITIONS',0,1,'L')
         pdf.set_font('Arial', '', 9)

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, '1.',0,0,'L')
         pdf.cell(60, 5, 'Authorise the minor variations to Development Approval [approval number] to allow for [title of section 84].',0,1,'L')

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, '2.',0,0,'L')
         pdf.cell(60, 5, 'Grant this Section 84 approval subject to compliance with all the following conditions and advice notes. All',0,1,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, '  ',0,0,'L')
         pdf.cell(60, 5, 'conditions and advice notes shall apply and remain in force for the duration of the approval period.',0,1,'L')



         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.set_font('Arial', 'B', 10)
         pdf.cell(60, 5, 'ADVISE TO APPLICANT',0,1,'L')
         pdf.set_font('Arial', '', 9)

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, '1.',0,0,'L')
         pdf.cell(60, 5, 'Authorise the minor variations to Development Approval [approval number] to allow for [title of section 84].',0,1,'L')

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, '2.',0,0,'L')
         pdf.cell(60, 5, 'Grant this Section 84 approval subject to compliance with all the following conditions and advice notes. All',0,1,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, '  ',0,0,'L')
         pdf.cell(60, 5, 'conditions and advice notes shall apply and remain in force for the duration of the approval period.',0,1,'L')

         pdf.cell(0,30,' ', 0,1,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'Stephen Dawson MLC',0,1,'L')
         pdf.set_font('Arial', 'B', 10)
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'MINISTER FOR ENVIRONMENT',0,1,'L')
         pdf.set_font('Arial', '', 9)
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(11, 5, 'DATE:',0,0,'L')
         pdf.cell(60, 5, '20 Feb 2018',0,1,'L')

         pdf.output('pdfs/approvals/3-approval.pdf', 'F')

    def generate_part5(self):

         pdf = FPDF('P', 'mm', 'A4')
         pdf.add_page()
         # pdf.image('plugins/flightsensation/images/flight_voucher.jpg', 0, 0, 210,297)

         #swan_canning_riverpark_dbca.png
         pdf.image('applications/static/images/swan_canning_riverpark_dbca.png', 30, 7, 144,24)

         pdf.set_font('Arial', 'I', 10)
         pdf.cell(0,33,' ', 0,1,'L')
         pdf.cell(0, 8, 'Swan and Canning Rivers Management Act 2006',0,1,'C')
         pdf.set_font('Arial', 'B', 10)
         pdf.cell(0, 8, 'PART 5',0,1,'C')
         pdf.set_font('Arial', 'BU', 10)
         pdf.cell(0, 8, 'DETERMINATION OF DEVELOPMENT APPLICATION',0,1,'C')
         pdf.set_font('Arial', '', 9)

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         #pdf.cell(6, 5, ' ',0,0,'L')
         #pdf.cell(60, 5, 'FILE NUMBER',0,0,'L')
         #pdf.cell(6, 5, ':',0,0,'L')
         #pdf.cell(6, 5, '1100',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'APPLICANT',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, 'JASON',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'APPLICANT\'S ADDRESS',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, '21 cars st kensington',0,1,'L')

         #pdf.cell(6, 5, ' ',0,0,'L')
         #pdf.cell(60, 5, 'LANDOWNER',0,0,'L')
         #pdf.cell(6, 5, ':',0,0,'L')
         #pdf.cell(6, 5, 'Bob Stans',0,1,'L')

         #pdf.cell(6, 5, ' ',0,0,'L')
         #pdf.cell(60, 5, 'LAND DESCRIPTION',0,0,'L')
         #pdf.cell(6, 5, ':',0,0,'L')
         #pdf.cell(6, 5, 'Its a park',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'DEVELOPMENT',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, 'yes developement allowed',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'VALID FORM 1 RECEIVED',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, 'Form 1 received yes',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'DETERMINATION',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.set_font('Arial', 'B', 9)
         pdf.cell(6, 5, 'APPROVAL WITH CONDITIONS',0,1,'L')
         pdf.set_font('Arial', '', 9)

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'The application to commence development in accordance with the information received on XX XX is',0,1,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'APPROVED subject to the following conditions:',0,1,'L')
         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.set_font('Arial', 'B', 10)
         pdf.cell(60, 5, 'Prior to the commencement of works',0,1,'L')
         pdf.set_font('Arial', '', 9)

         pdf.cell(0,2,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, '1.',0,0,'L')
         pdf.cell(60, 5, 'Approval to implement this decision is valid for two (2) years from the date of the approval.  If the development',0,1,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'has not been substantially commenced within this period, a new approval will be required before commencing or',0,1,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(10, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'or completing the development.',0,1,'L')

         pdf.cell(0,30,' ', 0,1,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'Stephen Dawson MLC',0,1,'L')
         pdf.set_font('Arial', 'B', 10)
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'MINISTER FOR ENVIRONMENT',0,1,'L')
         pdf.set_font('Arial', '', 9)
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(11, 5, 'DATE:',0,0,'L')      
         pdf.cell(60, 5, '20 Feb 2018',0,1,'L')
         
         pdf.output('pdfs/approvals/1-approval.pdf', 'F')

    def generate_permitold(self):
         pdf = FPDF('P', 'mm', 'A4')
         pdf.add_page()

         pdf.image('applications/static/images/parks_and_wildlife_service_dbca.jpg', 30, 7, 144,24)

         pdf.output('pdfs/approvals/1-permit-approval.pdf', 'F')


    def generate_permit(self):

         pdf = FPDF('P', 'mm', 'A4')
         pdf.add_page()
         # pdf.image('plugins/flightsensation/images/flight_voucher.jpg', 0, 0, 210,297)

         #swan_canning_riverpark_dbca.png
         pdf.image('applications/static/images/swan_canning_riverpark_dbca.png', 30, 7, 144,24)

    #     pdf.set_font('Arial', 'I', 10)
   #      pdf.cell(0, 33, ' ',0,0,'L')

#         pdf.cell(6, 5, ' ',0,0,'L')
 #        pdf.cell(0, 5, 'Pursuant to Part 4 (Regulation 29) of the Swan and Canning Rivers Management Regulations 2007, this ',0,1,'L')
  #       pdf.cell(6, 5, ' ',0,0,'L')
 #        pdf.cell(60, 5, 'APPROVED subject to the following conditions:',0,1,'L')
         # group spacer
 #        pdf.cell(0,5,' ', 0,1,'L')


         pdf.set_font('Arial', '', 10)
         pdf.cell(0,28,' ', 0,1,'L')
         pdf.cell(0, 5, 'Pursuant to Part 4 (Regulation 29) of the Swan and Canning Rivers Management Regulations 2007, this',0,1,'L')
         pdf.cell(0, 5, 'is to certify that a permit is issued to the person(s) or organisation described hereunder as permit holder',0,1,'L')
         pdf.cell(0, 5, 'and that person(s) or organisation is permitted to carry out the authorised works, acts or activities for',0,1,'L')
         pdf.cell(0, 5, 'duration specified, subject to the conditions listed below.',0,1,'L')

         pdf.cell(0,5,' ', 0,1,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'Permit holder',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, 'Jason Moore',0,1,'L')

         pdf.cell(0,5,' ', 0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'Authorised works, acts or activities',0,1,'L')
         pdf.cell(6, 5, '',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'Location of works, acts or activities:',0,1,'L')
         pdf.cell(6, 5, '',0,1,'L')


         pdf.cell(0,5,' ', 0,1,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(30, 5, 'Approval date:',0,0,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(50, 5, '10-Jan-2017',0,0,'L')

         pdf.cell(30, 5, 'Expiry date:',0,0,'L')
         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(30, 5, '10-Jan-2017',0,1,'L')

         # horizontal line
         pdf.line(7, 110, 205, 110)


         pdf.cell(0,15,' ', 0,1,'L')
         pdf.set_font('Arial', 'B', 10)

         pdf.cell(30, 8, 'CONDITIONS',0,1,'L')
         pdf.cell(10, 8, ' 1.',0,0,'L')
         pdf.cell(6, 8, ' ',0,0,'L')
         pdf.cell(200, 8, '',0,1,'L')

         pdf.cell(10, 8, ' 2.',0,0,'L')
         pdf.cell(6, 8, ' ',0,0,'L')
         pdf.cell(200, 8, '',0,1,'L')

         pdf.cell(10, 8, ' 3.',0,0,'L')
         pdf.cell(6, 8, ' ',0,0,'L')
         pdf.cell(200, 8, '',0,1,'L')


         pdf.cell(30, 8, 'ADVICE TO APPLICANT',0,1,'L')

         pdf.cell(10, 8, ' 1.',0,0,'L')
         pdf.cell(6, 8, ' ',0,0,'L')
         pdf.cell(200, 8, '',0,1,'L')

         pdf.cell(10, 8, ' 2.',0,0,'L')
         pdf.cell(6, 8, ' ',0,0,'L')
         pdf.cell(200, 8, '',0,1,'L')

         pdf.cell(10, 8, ' 3.',0,0,'L')
         pdf.cell(6, 8, ' ',0,0,'L')
         pdf.cell(200, 8, '',0,1,'L')


         pdf.cell(0,15,' ', 0,1,'L')
         pdf.set_font('Arial', '', 10)
         pdf.cell(30, 5, 'Glen Mcleod-Thorpe',0,1,'L')
         pdf.cell(30, 5, '13-Feb-2018',0,1,'L')



#      cell(0, 8, 'Swan and Canning Rivers Management Act 2006',0,1,'C')
#         pdf.set_font('Arial', 'B', 10)
#         pdf.cell(0, 8, 'PART 5',0,1,'C')
#         pdf.set_font('Arial', 'BU', 10)
#         pdf.cell(0, 8, 'DETERMINATION OF DEVELOPMENT APPLICATION',0,1,'C')
#         pdf.set_font('Arial', '', 9)

         # group spacer
         pdf.cell(0,5,' ', 0,1,'L')


         pdf.output('pdfs/approvals/2-approval.pdf', 'F')

    def get(self,app,self_view,context):
        request = self_view.request

        return context



