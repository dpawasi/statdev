from __future__ import unicode_literals
from .models import Location, Record, PublicationNewspaper, PublicationWebsite, PublicationFeedback,Referral,Application, Delegate, Compliance
from django.utils.safestring import SafeText
from django.contrib.auth.models import Group
from django.db.models import Q
from applications.email import sendHtmlEmail, emailGroup, emailApplicationReferrals
from fpdf import FPDF

class PDFtool():

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

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'FILE NUMBER',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, '1100',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'APPLICANT',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, 'JASON',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'APPLICANT\'S ADDRESS',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, '21 cars st kensington',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'LANDOWNER',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, 'Bob Stans',0,1,'L')

         pdf.cell(6, 5, ' ',0,0,'L')
         pdf.cell(60, 5, 'LAND DESCRIPTION',0,0,'L')
         pdf.cell(6, 5, ':',0,0,'L')
         pdf.cell(6, 5, 'Its a park',0,1,'L')

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

    def generate_permit(self):
         pdf = FPDF('P', 'mm', 'A4')
         pdf.add_page()

         pdf.image('applications/static/images/parks_and_wildlife_service_dbca.jpg', 30, 7, 144,24)

         pdf.output('pdfs/approvals/1-permit-approval.pdf', 'F')

    def get(self,app,self_view,context):
        request = self_view.request

        return context



