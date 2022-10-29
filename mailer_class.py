import sys
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders

class Mailer():
    '''
    Mailer is a self-contained class for manipulating with various mail functions and send email alerts 
    The class is instantiated with a kwargs call to the locals() function in iPython/Jupyter, or by 
    manually loading all relevant member variables with the member refresh_vars() function. 
    
    Functions:
    __init__
        
        Arguments:
            **kwargs -- a dictionary of key-value pairs
            
        Returns
    '''
    vars = dict()
    def __init__(self):
        pass
        return None
    
    def Mailer_Setting(self,**kwargs):
        self.vars.clear()
        if kwargs is not None:
            self.refresh_vars(**kwargs)
        return None
    
    def refresh_vars(self,**kwargs):
        if kwargs is not None:
            for key, value in kwargs.items():
                self.vars[key] = value
        return None
    
    def drop_dup_html(df):
        '''
		Helper function to drop duplicates from a dataframe and convert the dataframe to HTML
		for further processing as an email alert
		Input  - dataframe
		
		eg:
		email_body =  'Tables Used in deconfig: \n' + drop_dup_html(df_original) + '<br />' +\
                'Tables With Indexes: \n' + drop_dup_html(df) + '<br />' + 'Tables with no Index: ' +\
                 df_noindex['Table_Name'].to_string(index=False) + '<br />'
        '''
        email_html_f = "{df}"
        email_html_f = email_html_f.format(df=df.drop_duplicates().to_html(index=False))
        return email_html_f
	
    def highlight_cellss(val,color = 'yellow'):
        '''
		Helper function to highlight a record in a dataframe when a value is 1. 
		Will be imporved further to accept various conditions
		
		eg:
			 html = df.style.applymap(highlight_cell,subset = ['your-column-name'])
 
	    '''
        if val == 1:
            return 'background-color : %s' % color
        else:
            return ''
			
    def highlight_blanks(val,color = 'red'):
        '''
		Helper function to highlight a record in a dataframe when a value is blank. 
		Will be imporved further to accept various conditions.
		
		Use the builtin stuler function highlight_null for a dataframe when using on NaN
		
		eg:
			 html = df.style.applymap(highlight_blanks,subset = ['your-column-name'])
 
	    '''
        if val == '':
            return 'background-color : %s' % color
        else:
            return ''
		
    def send_mail_html(self,subject,email_body,**kwargs):
        '''
		Helper function to send an email with the specified subject and body as HTML content
		Input  - subject, email_body - which will be a HTML code
		
		eg:
			subject = "Runtime lookups - Tables without indexes"
			send_mail(subject,email_body)
	    '''
        self.refresh_vars(**kwargs)
#        if kwargs:
#            #self.refresh_vars(**kwargs)
#            email_from = self.vars['Email_From']
#            email_to = self.vars['Email_To']
#            email_cc = self.vars['Email_CC']            
#          
#        else:
#            
#            email_from = self.vars['Email_From']
#            email_to = self.vars['Email_To']
#            email_cc = self.vars['Email_CC'] 
#            email_bcc = self.vars['Email_BCC']
        
        email_from = self.vars['Email_From']
        email_to   = self.vars['Email_To']
        email_cc   = self.vars['Email_CC'] 
         #email_bcc  = self.vars['Email_BCC']
    
        msg = MIMEMultipart('alternative')
        msg['From'] = email_from
        msg['Subject'] = subject
        msg['To'] = email_to
        msg['Cc'] = email_cc
        
        #part1 = MIMEText(email_body_plain, 'plain')
        part1 = MIMEText(email_body, 'html')

        msg.attach(part1)
        
        server = smtplib.SMTP(self.vars['SMTP_HOST'])
        if email_cc =='' or email_cc is None:
            to_address = [email_to]
        else:
            to_address = [email_to] + [email_cc]
        server.sendmail(email_from, msg['To'].split(";")+msg['Cc'].split(";") , msg.as_string())
        server.quit()

    def send_mail_csv(self, subject, email_body,csv_filename, **kwargs):
        '''
		Helper function to send an email with the specified subject and body and csv file
		Input  - subject, email_body - which will be a HTML code

		eg:
			subject = "Runtime lookups - Tables without indexes"
			send_mail(subject,email_body)
	    '''
        self.refresh_vars(**kwargs)
        email_from = self.vars['ETL_Email_From']
        email_to = self.vars['ETL_Email_To']
        email_cc = self.vars['ETL_Email_CC']
        email_bcc = self.vars['ETL_Email_BCC']

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = email_from
        msg['To'] = email_to
        msg['CC'] = email_cc

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(csv_filename, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=csv_filename)  # or
        msg.attach(part)

        part1 = MIMEText(email_body, 'html')
        msg.attach(part1)

        server = smtplib.SMTP(self.vars['SMTP_HOST'])
        if email_cc =='' or email_cc is None:
            to_address = [email_to]
        else:
            to_address = [email_to] + [email_cc]
        #to_address = [email_to] + [email_cc] + [email_bcc]
        server.sendmail(email_from, msg['To'].split(";")+msg['Cc'].split(";"), msg.as_string())
        server.quit()
        
	
    
    def send_mail_Attachment(self, subject, email_body, files, **kwargs):
        '''
		Helper function to send an email with the specified subject and body and csv file
		Input  - subject, email_body - which will be a HTML code

		eg:
			subject = "Runtime lookups - Tables without indexes"
			send_mail(subject,email_body)
	    '''
        self.refresh_vars(**kwargs)
        
#        if kwargs:
#            email_from = self.vars['ETL_Email_From']
#            email_to = self.vars['Email_To']
#            email_cc = self.vars['Email_CC']
#            
#        else:
#            
#            email_from  = self.vars['ETL_Email_From']
#            email_to 	= self.vars['ETL_Email_To']
#            email_cc 	= self.vars['ETL_Email_CC'] 
#            email_bcc 	= self.vars['ETL_Email_BCC']
        email_from = self.vars['Email_From']
        email_to   = self.vars['Email_To']
        email_cc   = self.vars['Email_CC']
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] 	= subject
        msg['From'] 	= email_from
        msg['To'] 		= email_to
        if email_cc =='' or email_cc is None:
            msg['CC']		= ''
        else:
            msg['CC']		= email_cc

        #part = MIMEBase('application', "octet-stream")
        #part.set_payload(open(csv_filename, "rb").read())
        #encoders.encode_base64(part)
        #part.add_header('Content-Disposition', 'attachment', filename=csv_filename)  # or
        #msg.attach(part)

        part1 = MIMEText(email_body, 'html')
        msg.attach(part1)
        
        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(fil.read(),Name=basename(f))
        # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)
		

        server = smtplib.SMTP(self.vars['SMTP_HOST'])
        if email_cc =='' or email_cc is None:
            to_address = [email_to]
        else:
            to_address = [email_to] + [email_cc]
			
        server.sendmail(email_from, msg['To'].split(";")+msg['CC'].split(";"), msg.as_string())
        server.quit()
