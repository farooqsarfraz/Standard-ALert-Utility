# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 13:13:10 2020

@author: ishtisa
"""

import pandas as pd
import numpy as np
import sys
import os
import Configuration_Read_Validation_Class
from importlib import reload 
import mailer_class
import ast

reload(Configuration_Read_Validation_Class)
reload(mailer_class)
global mysql_conn ,mysql_conn1

os.chdir(os.path.dirname(os.path.abspath(__file__)))
class Alerts():
    
    C = Configuration_Read_Validation_Class.Configration_Read_Validation()
    M = mailer_class.Mailer()
    Config= dict()

    
    HTML_Header = """<HTML>
     <HEAD>
    <style type=\"text/css\">.table
	{
	width:100%;
	border-collapse:collapse;
    
	}
	.table
    td
	{
	padding:7px;
	border:#000000 1px solid;


	text-align: center;
	font-size: 10px;
	}
	.table
    tr{
	background:#ffffff;

	color:#000066;
	}
	.table
    th{
	background:#000000 ;
	text-align: center;
    border:#ff0000 1px solid;
	padding;25%;
    color: white;
	font-size: 13px;
 
	}
    </style>
    </HEAD>"""

    
    def __init__(self):
        self.Config_Setting()
        return None
    
    def Config_Setting(self):
        Status , Return_Arg = self.C.Read_Configuration("Jconfig.json")
        self.M.Mailer_Setting(**self.C.config_dict['EmailInfo'])
        Red_Blue_Status=self.C.config_dict['ClientDetails']['Red_Blue_Status']
        if Red_Blue_Status.lower()=='y':
            Email_Subject1 = self.C.config_dict['ClientDetails']['Clientname'].upper()+""" - """+self.C.config_dict['ClientDetails']['Team'].upper()+""" | Json Config Error """
        else:
            Email_Subject1 = self.C.config_dict['ClientDetails']['Clientname'].upper()+""" | Json Config Error """

        if not Status:
            Email_Msg = Return_Arg
            print(Email_Msg)
            self.M.send_mail_html(Email_Subject1,str(Email_Msg))
            sys.exit(0)
        
    
    def Table_Header_HTML(self,Table_Heading,dfResult):
        
        ''' 
        Helper function to read the column names of given data frame, 
        generate the Table header HTML of all columns and return HTML text as String.
        
        eg:
            Table_Header_HTML(Table_Heading, Dataframe)
        
        Result:
            
            <h1>Table_Heading</h1> <tr> <th>Col1</th> <th>Col2</th> <th>Col3</th> ... </tr>
            
        '''
        
        Table_Heading_HTML =  "<h3 style=\"text-align:center ; color:#000000;\">"+ Table_Heading + " </h3>\n<table style=\"width:100%\" class=\"table\">\n"
        
        Table_Heading_HTML = Table_Heading_HTML  + '\n<tr>\n'
        for position in range(len(dfResult.columns)):
            Table_Heading_HTML = Table_Heading_HTML + '\n<th>\n' +  dfResult.columns[position]  + '\n</th>\n'           # Table Header HTML Setting
        Table_Heading_HTML = Table_Heading_HTML  + '\n</tr>\n'
        
        return Table_Heading_HTML
    
    
    
    def Complete_Alert (self,AlartParam ,**Kwarg):
        
        ''' 
        Helper function to generate the complete HTML alert containing one or more
        ( Simple/Custom ) HTML tables depending upon the given configuration of passed alert name.
        
        eg:
            Complete_Alert( Alert Name)
        Result:    
            <HTML> <Body> <Table 1 Header> <Table1> ... </Table1> <Table 2 Header> <CustomTable2> ... </CustomTable2> ...
            </Body> </HTML>
        '''
        print("Generating Alert ... ")
        
        try:
            
            self.config ={}
            self.Read_Configuration(AlartParam, **Kwarg)
            dfCustomization= self.config["Custom_Checks"]
            dfQueries= self.config["dfQueries"]
            FolderPath= self.config["FolderPath"]
            Email_Subject= self.config["Email_Subject"]
            Is_Attachment= self.config["Is_Attachment"]
            
            Alert=""
        
            if (len(dfQueries.index)>0):
            
                self.Query_Results()
                Queries_Results_dt= self.config["Queries_Results_dt"]

                for Table_Heading,dfResult in Queries_Results_dt.items():
                    dfCurrentTableCustomization = dfCustomization[dfCustomization['filename']==Table_Heading]
                    if dfCurrentTableCustomization.empty:
                        Alert = Alert + self.Simple_alert(Table_Heading,dfResult)
                    else:
                        status,html = self.Custom_alert(Table_Heading,dfResult,dfCurrentTableCustomization)
                        if status:
                            Alert = Alert + html
                        else:
                            Email_Msg = "Error: "+html +" Table '"+Table_Heading +"'."
                            print(Email_Msg)
                            self.M.send_mail_html(Email_Subject+" | Error",str(Email_Msg),**Kwarg)
                            sys.exit(0)
        
                Alert = self.HTML_Header + "\n<body>\n\n" + Alert + "\n</body>\n</HTML><BR><BR>"
        
            else:
                Email_Msg = "No Query is found in mentioned Directory.\n" + "Directory Path: " + str(FolderPath) + "\nPlease check the Folder Path Or File!)"
                print(Email_Msg)
                self.M.send_mail_html(Email_Subject+" | Error",str(Email_Msg),**Kwarg)
                sys.exit(0)
        
            recipient = { key:value for key,value in self.config.items() if key in ['Email_To','Email_CC']}
            
            #print(recipient)
            
            if Is_Attachment:
                self.C.CreateDirectories('HTML_Alerts')
                if Is_Attachment[0] == "1":
                    html_file = "HTML_Alerts/"+Email_Subject.strip().replace('|','-')+".html"
                    f = open( html_file, "w")
                    f.write(str(Alert))
                    f.close()
                    Is_Attachment[0] = html_file
                elif Is_Attachment[0] == "0":
                    del Is_Attachment[0]
                self.M.send_mail_Attachment(Email_Subject,str(Alert),Is_Attachment,**recipient)
            else:
                self.M.send_mail_html(Email_Subject,str(Alert),**recipient)
            print("Alert is Generated!")
        
        finally:
            pass
            #mysql_conn1.close()
            #stg.close()
            

    
    def Simple_alert(self,Table_Heading,dfResult):
        
        ''' 
        Helper function to generate the simple HTML Table text from the given dataframe 
    
        eg:
            Simple_alert (Table_Heading , Result Dataframe)
            
        Result:
            
            <h1>Table_Heading</h1> <Table> <tr> <th>Col1</th> <th>Col2</th> <th>Col3</th> ... </tr>
            <tr> <td>Col1</td> <td>Col2</td> ... </tr> ...  </Table> 
        '''
        
        Table_HTML =""
        Table_Body_HTML=""
        Table_Heading_HTML = self.Table_Header_HTML(Table_Heading,dfResult)
        #print(dfResult)
        nRows = len(dfResult.index)
        j=0
        while j < nRows:
            Table_Body_HTML = Table_Body_HTML  + '\n<tr>\n'
            for i in dfResult.columns:
                #print(i)
                Table_Body_HTML= Table_Body_HTML  + '\n<td>\n' +  str(dfResult[i][j]) + '\n</td>\n'
            Table_Body_HTML = Table_Body_HTML  + '\n</tr>\n'
            j=j+1
        
        Table_HTML = Table_Heading_HTML + Table_Body_HTML +   "\n</table><BR><BR>\n\n"
        
        return Table_HTML
    
    
    
    def Custom_alert(self,Table_Heading,dfResult,dfCustomization ):
        
        ''' 
        Helper function to generate the Custom HTML text from the given dataframe 
        
        eg:
            Custom_alert (Table_Heading , Result Dataframe , Custimization Dataframe)
            
        Result:
            
            <h1>Table_Heading</h1> <Table> <tr> <th>Col1</th> <th>Col2</th> <th>Col3</th> ... </tr>
            <tr> <td>Col1</td> <td>Col2</td> ... </tr> ...  </Table>
        
        '''
        
        Table_HTML =""
        Table_Body_HTML=""
        Table_Heading_HTML = self.Table_Header_HTML(Table_Heading,dfResult)
        df= dfResult
        Total_Checks = len(dfCustomization)
        Customization_dt = dfCustomization.to_dict('records')
        Customization_list = dfCustomization.to_dict('list')
        for rows in range(Total_Checks):
            Staus, df = self.Customization(df,Customization_dt[rows])
            if not Staus:
                return Staus, df

        nRows = len(df.index)
        j=0
        while j < nRows:
            Table_Body_HTML = Table_Body_HTML  + '\n <tr> \n'
            for i in df.columns:
                if i in Customization_list["Col1"]:
                    Table_Body_HTML= Table_Body_HTML +  str(df[i][j])
                    
                else:
                    Table_Body_HTML= Table_Body_HTML  + '\n <td> \n' +  str(df[i][j]) + '\n </td> \n'
            Table_Body_HTML = Table_Body_HTML  + '\n</tr>\n'
            j=j+1
        
        Table_HTML = Table_Heading_HTML + Table_Body_HTML +   "\n</table><BR><BR>\n\n"
        
        return True, Table_HTML
        
    def replaceMultiple(self,df, toBeReplaces, newString):
        for elem in toBeReplaces :
                df = df.fillna(0).astype(str).str.replace(elem, newString)
        return  df.str.strip()
    
    def CheckFloat(self, s):
        try: 
            #float(s)
            pd.to_numeric(s, errors='coerce').notnull().all()
            return True
        except ValueError:
            return False 
    
    
    def Customization(self,df, dt ):
        
        ''' 
        Helper function to apply given customization on the given dataframe 
        
        eg:
            Customization (Dataframe , Custimization Dictionary )
        '''
        Error_Msg =''
        if isinstance(dt, dict):
            comparision = dt["comparision"]
            Com_type = dt["Com_type"]
            Col1 = dt["Col1"]
            Col2 = dt["Col2"]
            Mul = dt["Mul"]
            RBGColor = dt["RBGColor"]
            
            if comparision.lower() == "b":
                Bet_val= Col2.split("&")
                Bet_val1 = Bet_val[0].strip()
                Bet_val2 = Bet_val[1].strip()
            
            
            #print(comparision ,Com_type ,Col1 , Col2 ,Mul ,RBGColor)
            #print(df[Col1])
            
        elif isinstance(dt, pd.DataFrame):
            comparision = "Dataframe"
            RBGColor = "#f70431"
        
        pattern = [',', '$']
        #print(Col1)
        
        
        if Col1 not in df.columns:
            Error_Msg= "The follwing column '"+Col1+"' is not present in the"
            return False, Error_Msg
        if Com_type == "2":
            if ((comparision.lower()!= "b") and( Col2 not in df.columns)):
                Error_Msg= "The follwing column '"+Col2+"' is not present in the"
                return False, Error_Msg
            elif ((comparision.lower()== "b") and (Bet_val1 not in df.columns)):
                Error_Msg= "The follwing column '"+Bet_val1+"' is not present in the"
                return False, Error_Msg
            elif ((comparision.lower()== "b") and (Bet_val2 not in df.columns)):
                Error_Msg= "The follwing column '"+Bet_val2+"' is not present in the"
                return False, Error_Msg
        

        if not self.CheckFloat(self.replaceMultiple(df[Col1],pattern,'')) and comparision in ['>','<','>=','<=','B','b'] :
            Error_Msg= "The column values should be integers or float type for this comparision.\nThe follwing comparision '"+comparision+"' is not allowed for column: '" +Col1 +"' for"
            return False, Error_Msg
        if Com_type ==2:
            if not self.CheckFloat(self.replaceMultiple(df[Col2],pattern,'')) and comparision in ['>','<','>=','<=','B','b']:
                Error_Msg= "The column values should be integers or float type for this comparision.\nThe follwing comparision '"+comparision+"' is not allowed for column: '" +Col2 +"' for"
                return False, Error_Msg

        if Com_type=="1":
            if comparision== ">=":
                df[Col1] = np.where(pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float") >= float(Col2)*Mul,
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '\n</td>\n' ,
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
                
            elif comparision=="<=":
                df[Col1] = np.where(pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float") <= float(Col2)*Mul,
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '\n</td>\n',
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
                
            elif comparision==">":
                df[Col1] = np.where(pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float") > float(Col2)*Mul,
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '\n</td>\n',
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
                
            elif comparision=="<":
                df[Col1] = np.where(pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float") < float(Col2)*Mul,
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '</td>\n',
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
                
            elif comparision=="=":
                df[Col1] = np.where(df[Col1]== str(Col2),
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '\n</td>\n',
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
            
            elif comparision.lower()=="b":
                df[Col1] = np.where((pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float") < float(Bet_val1) ) | (pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float") > float(Bet_val2)) ,
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '\n</td>\n',
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
                
        elif Com_type=="2":  
            if comparision== ">=":
                df[Col1] = np.where(pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float")>= (pd.to_numeric(self.replaceMultiple(df[Col2],pattern,''), downcast ="float")*Mul),
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '\n</td>\n',
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
                
            elif comparision=="<=":
                df[Col1] = np.where(pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float") <= (pd.to_numeric(self.replaceMultiple(df[Col2],pattern,''), downcast ="float")*Mul),
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '\n</td>\n',
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
        
            elif comparision==">":
                df[Col1] = np.where(pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float") > (pd.to_numeric(self.replaceMultiple(df[Col2],pattern,''), downcast ="float")*Mul),
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '\n</td>\n',
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
        
            elif comparision=="<":
                df[Col1] = np.where(pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float") < (pd.to_numeric(self.replaceMultiple(df[Col2],pattern,''), downcast ="float")*Mul),
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '</td>\n',
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
        
            elif comparision=="=":
                df[Col1] = np.where(df[Col1] == df[Col2],
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '\n</td>\n',
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
                
            elif comparision.lower()=="b":
                df[Col1] = np.where((pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float") < pd.to_numeric(self.replaceMultiple(df[Bet_val1],pattern,''), downcast ="float")) | (pd.to_numeric(self.replaceMultiple(df[Col1],pattern,''), downcast ="float") > pd.to_numeric(self.replaceMultiple(df[Bet_val2],pattern,''), downcast ="float"))  ,
                  '\n<td bgcolor='+ RBGColor+ '>\n' +  df[Col1].astype(str) + '\n</td>\n',
                  '\n<td>\n' +  df[Col1].astype(str) + '\n</td>\n')
                
            
                
        elif comparision== "Dataframe":
            
            nRows = len(df.index)
            j=0
            while j < nRows:
                for i in df.columns:
                    if str(dt[i][j]) =="1":
                        df[i][j] = '\n<td bgcolor='+ RBGColor+ '>\n' +   str(df[i][j]) + '\n</td>\n'
                    else:
                        df[i][j]  = '\n<td>\n' +  str(df[i][j]) + '\n</td>\n'
                j=j+1

        
        return True, df
    
    
    
    def Read_Configuration(self, AlertParam, **Kwargs):
        
        ''' 
        Helper function to read configuration from database for requested alert. 
        
        eg:
            Read_Configuration ( 'Gain Alert' )
        
        '''
        Server = str(self.C.config_dict['ClientDetails']['Alert_Config_detail'][0])
        DB = str(self.C.config_dict['ClientDetails']['Alert_Config_detail'][1])
        
        ClientName = ""
        DBDetail= "\nServer: "+Server.upper()+ "\nTable Name: "+DB+".`da.Alert_config`"
        if self.C.config_dict['ClientDetails']['Team'] is None or self.C.config_dict['ClientDetails']['Team'] =="":
            ClientName = str(self.C.config_dict['ClientDetails']['Clientname'].upper())
        else:
            ClientName = str(self.C.config_dict['ClientDetails']['Clientname'].upper()+""" - """+self.C.config_dict['ClientDetails']['Team'].upper())
        
        
        if AlertParam != "" and not Kwargs:
            
            Query="Select * from "+DB+".`da.Alert_config` where Alert = '"+ AlertParam + "';"
			
            try:
                self.C.Create_Connection(Server)
                stg = self.C.Connections[Server]
                df_data=pd.read_sql(Query,stg)
                Config_dict = df_data.to_dict('list')
			
            except Exception as e:
                Email_Msg= "Failed to run the Config Query \n\n Please check the Database Configuration."+DBDetail
                print(Query)
                Email_Msg = Email_Msg + str(self.Error_Msg(e))
                print(Email_Msg)
                Subject = ClientName + " | Database Configuration Read Error"
                self.M.send_mail_html(Subject,str(Email_Msg))
                sys.exit(0)
            finally:
                self.C.Close_Connection(Server)
                
			
            if df_data.empty:
                Email_Msg= ("Alert Name: '" +AlertParam+ "' Not Found in Database Configuration !"+DBDetail)
                print(Email_Msg)
                Subject = ClientName + " | Database Configuration Not Found"
                self.M.send_mail_html(Subject,str(Email_Msg))
                sys.exit(0)
					
            else:
				
                self.config.update ( { "Alert"          : Config_dict['Alert'][0]                   } )
                self.config.update ( { "ServerType"     : Config_dict['ServerType'][0].lower()      } )
                self.config.update ( { "FolderPath" 	  : Config_dict['FolderPath'][0] 	          } )
                self.config.update ( { "Email_To" 		  : Config_dict['Email_To'][0]  		          } )
                self.config.update ( { "Email_CC" 		  : Config_dict['Email_CC'][0]     	          } )
                self.config.update ( { "Email_Subject"  : Config_dict['Email_Subject'][0]           } )
                self.config.update ( { "Ordered"        : Config_dict['Ordered'][0]                 } )
                if Config_dict['Query'][0] is None or Config_dict['Query'][0]=='':
                    self.config.update ( { "Query"      : Config_dict['Query'][0]                   } )
                else:  
                    self.config.update ( { "Query"      : ast.literal_eval(Config_dict['Query'][0]) } )
                self.config.update ( { "Is_Attachment"  : [Config_dict['Is_Attachment'][0]]         } )
                self.config.update ( { "Is_Active"      : Config_dict['Is_Active'][0]               } )
                Custom_Checks = Config_dict['Custom_Checks'][0]
                
				
        elif Kwargs:
            self.config.update ( { "Alert" 			 : Kwargs['Alert']  			  } )
            self.config.update ( { "ServerType" 	 : Kwargs['ServerType'].lower()  	  } )
            self.config.update ( { "FolderPath" 	 : Kwargs['FolderPath']		  } )
            self.config.update ( { "Email_To" 		 : Kwargs['Email_To']		  } )
            self.config.update ( { "Email_CC" 		 : Kwargs['Email_CC']		  } )
            self.config.update ( { "Email_Subject"  : Kwargs['Email_Subject']   } )
            self.config.update ( { "Ordered"        : Kwargs['Ordered']         } )
            self.config.update ( { "Query"          : Kwargs['Query']           } )
            self.config.update ( { "Is_Attachment"  : Kwargs['Is_Attachment']   } )
            Custom_Checks = Kwargs['Custom_Checks']  
        
        if self.config["Is_Active"]== 0:
            
            Email_Msg= ("Alert Name: '" +AlertParam+ "' is not Active !"+DBDetail)
            print(Email_Msg)
            Subject = ClientName + " | Database Configuration - Alert is not Active"
            self.M.send_mail_html(Subject,str(Email_Msg))
            sys.exit(0)
            
        #print(self.config["Query"])
        dfCustom_Checks = pd.DataFrame(columns=['filename','Col1','Col2','comparision','Com_type', 'RBGColor' , 'Mul'])
        if Custom_Checks != "":
		
            All_Custom_Checks=Custom_Checks.split("|")
            for k in range(len(All_Custom_Checks)):
                filename,Col1,Col2,comparision,Com_type, RBGColor = All_Custom_Checks[k].split(":")
                filename=str(filename).strip()
                Col1=str(Col1).strip()
                Col2=str(Col2).strip()
                comparision=str(comparision).strip()
                Com_type=str(Com_type).strip()
                RBGColor=str(RBGColor).strip()
                if RBGColor.lower()=="default":
                    RBGColor =  "#f70431"
                if len(comparision) > 2 and comparision[1]=="=":
                    Mul = float(comparision[2:])
                    comparision = comparision[0:2]
                elif len(comparision) == 2 and comparision[1]=="=":
                    Mul = 1.0
                    comparision = comparision[0:2]
                elif len(comparision) >1:
                    Mul = float(comparision[1:])
                    comparision = comparision[0]
                else:
                    Mul=1.0
               # print(Mul)	
                #print(comparision)
                dfCustom_Checks.loc[k]=[filename,Col1,Col2,comparision,Com_type,RBGColor,Mul]
				
            self.config.update ( { "Custom_Checks" : dfCustom_Checks } )
				
        else:
            self.config.update ( { "Custom_Checks" : dfCustom_Checks } )
            
        if self.config["ServerType"] not in ["ai","arch","prod","stg"]:
            Email_Msg= ("Server Type information is not correct in database Configuration.\nPlease select any one from the below list: \n'ai' : For Ai Server. \n'arch' : For Archival Server \n'prod' : For Production Server \n'stg' For Staging Server \n"+DBDetail)
            print(Email_Msg)
            Subject = ClientName + " | Database Configuration Error for ServerType"
            self.M.send_mail_html(Subject,str(Email_Msg))
            sys.exit(0)
					
        self.Read_Alert_Queries()
        
    
				
    
    def CheckInt(self, s):
        try: 
            int(s)
            return True
        except ValueError:
            return False 
    
    
    def Read_Alert_Queries(self):
        
        ''' 
        Helper function to read all the query files placed in given folder path. 
        
        eg:
            Read_Alert_Queries ()
        
        '''
        dfQueries=pd.DataFrame(columns=['ordered','FileName','Query'])
        FolderPath = self.config["FolderPath"]
        Query = self.config["Query"]
        Alert = self.config["Alert"]
        Ordered = self.config["Ordered"]
        
        i=0
        if FolderPath!="":
            for Path, dirs, files in os.walk(FolderPath, topdown=False ):
                for filename in files:
                    if Path == FolderPath:
                        ff=os.path.join(Path, filename)
                        file=open(ff,'r')
                        fs=file.read()
                        if (Ordered):
                            ss= filename.find('_')
                            if (self.CheckInt(filename[:ss]) ):
                                #print(int(filename[:ss]),filename)
                                dfQueries.loc[i]=[int(filename[:ss]),filename[ss+1:].replace(".txt",""),fs.replace("'%","'%%").replace("%'","%%'")]
                            else:    
                                dfQueries.loc[i]=[0,filename.replace(".txt",""),fs.replace("'%","'%%").replace("%'","%%'")]
                        else:    
                            dfQueries.loc[i]=[0,filename.replace(".txt",""),fs.replace("'%","'%%").replace("%'","%%'")]
                        i=i+1
                        file.close()
        else:
            nsize=len(Query)
            #print(type(Query))
            #print(Query)
            #print(nsize)
            
            if isinstance(Query, dict):
                while i <  nsize:
                    dfQueries.loc[i]=[i+1,Query[i+1][0],Query[i+1][1].replace("'%","'%%").replace("%'","%%'")]
                    i=i+1
            else:
                dfQueries.loc[i]=[0,Alert,Query.replace("'%","'%%").replace("%'","%%'")]
        dfQueries.sort_values(by=['ordered'],ascending=True,
                                      inplace=True, na_position='first')
        dfQueries.reset_index(drop=True, inplace=True)
        self.config.update ( { "dfQueries" : dfQueries } )
	
    
    
    def Query_Results(self):
        ''' 
        Helper function to execute given queries at DB and stores its result into a dictionary. 
        
        eg:
            Query_Results ()
            
        Result:
            
        {FileName:FileQueryResult_Dataframe , ...}
        
        '''
        Queries_Result_dict={}
        dfQueries= self.config["dfQueries"]
        Email_Subject= self.config["Email_Subject"]
        ServerType= self.config["ServerType"].lower()
        #print(ServerType)
        
        
        i=0
        while (i < len(dfQueries.index)):
            
            FileName = dfQueries['FileName'][i]
            Query = dfQueries['Query'][i]
            try:
                self.C.Create_Connection(ServerType)
                stg = self.C.Connections[ServerType]
                dfdata  = pd.read_sql(Query,stg)
            except Exception as e:
                Email_Msg = ("Failed to run the query.<BR><BR> File Name: " +str(FileName)+ "<BR><BR> Exception: "+ str(e)+"<BR><BR> Query = "+ str(Query))
                print(Email_Msg)
                self.M.send_mail_html(Email_Subject,str(Email_Msg))
                sys.exit(0)
            finally:
                self.C.Close_Connection(ServerType)
                
            Queries_Result_dict.update({FileName:dfdata})
            i=i+1
        
            
        self.config.update ( { "Queries_Results_dt" : Queries_Result_dict } )
        
    def Error_Msg(self , e):
        Message = "Error code: "+ str(e.errno)  + "\n" # error number
        Message = Message + "SQLSTATE value: "+ str(e.sqlstate) +"\n"  # SQLSTATE value
        Message = Message + "Error message:", str(e.msg) +"\n"         # error message
        Message = Message + "Error:", str(e)  +"\n"                    # errno, sqlstate, msg values
        return Message
    
    
    
    def Sensor_Alert(self,ProgramID,Sensor_Type,NDays):
        
        #ProgramID
        if NDays is None or NDays=="":
            NDays = "10"
        else:
            NDays = str(NDays)
            
        if Sensor_Type is None or Sensor_Type =="":
            Sensor_Type = "Overall"
            Sensor_Type1 = " - Overall"
        else:
            Sensor_Type1 = " - " + Sensor_Type
            
            
        Lag = str(Q.vars["Data_Lag"])
        clientname = str(Q.vars["clientname"])
            
        query=""
        if Sensor_Type == "Overall":
            query = """select distinct Sensors_Name, Sensors_Category 
                        from `etl.cc_sensors_config` 
                        where ProgramID in ('"""+ProgramID+"');"

        else :
            query = """select distinct Sensors_Name, Sensors_Category
                        from `etl.cc_sensors_config`
                        where ProgramID in ('"""+ProgramID+"')   and Sensors_For = '"+Sensor_Type+"';"
                        
        try:
            dfSensorConfig  = pd.read_sql(query,mysql_conn)
        except Exception as e:
            Email_Msg = ("Failed to run the query.<BR><BR> Exception: "+ str(e)+"<BR><BR> Query = "+ str(query))
            print(Email_Msg)
            Email_Subject = "Sensor data Read query Failed" + Sensor_Type
            M.send_mail_html(Email_Subject,str(Email_Msg))
            sys.exit(0)  
        
        if dfSensorConfig.empty:
            pass
        else:
            
            Sensors_Names = ' ,'.join('"{0}"'.format(w) for w in dfSensorConfig['Sensors_Name'].tolist())
            #print(Sensors_Names)
             
            query ="""select TRIM(Sensors_Date) as Sensors_Date,upper(TRIM(ProgramID)) as ProgramID,upper(TRIM(CustomGroup1)) as CustomGroup1,upper(TRIM(CustomGroup2)) as CustomGroup2 ,Sensors_Name, case when Sensors_Category=1 then Sensors_Value_Num when Sensors_Category=2 then Sensors_Value_Text end as Sensors_Value_NumT ,Sensors_Flag FROM `etl.cc_sensors_data` 
                                WHERE ProgramID IN ('"""+ProgramID+"""')
                                AND Sensors_Date between date_sub( curdate(), interval """+NDays+""" day )  
                                AND date_sub( curdate(), interval """ + Lag + """ day )
                                AND Sensors_Name in ("""  + Sensors_Names + """)
                                GROUP BY 1,2,3,4,5
                                ORDER BY 1,2,3,4,5"""

            try:
                dfSensorData  = pd.read_sql(query,mysql_conn)
            except Exception as e:
                Email_Msg = ("Failed to run the query.<BR><BR> Exception: "+ str(e)+"<BR><BR> Query = "+ str(query))
                print(Email_Msg)
                Email_Subject = "Sensor data Read query Failed - " + Sensor_Type
                M.send_mail_html(Email_Subject,str(Email_Msg))
                sys.exit(0) 
                
            dfPivotDate_Value =  dfSensorData.groupby(["Sensors_Date","ProgramID","CustomGroup1","CustomGroup2","Sensors_Name"])['Sensors_Value_NumT'].sum().unstack(fill_value='NA').reset_index().rename_axis(None, axis=1)
            dfPivotDate_Sensor = dfSensorData.groupby(["Sensors_Date","ProgramID","CustomGroup1","CustomGroup2","Sensors_Name"])['Sensors_Flag'].sum().unstack(fill_value='NA').reset_index().rename_axis(None, axis=1)
            
            alertdf = self.Customization(dfPivotDate_Value, dfPivotDate_Sensor )
        
        Table_Heading = "Sensor Alert" + Sensor_Type1
        Table_HTML =""
        Table_Body_HTML=""
        Table_Heading_HTML = self.Table_Header_HTML(Table_Heading,alertdf)

        nRows = len(alertdf.index)
        j=nRows -1
        while j >= 0:
            Table_Body_HTML = Table_Body_HTML  + '\n <tr> \n'
            for i in alertdf.columns:
                    Table_Body_HTML= Table_Body_HTML +  str(alertdf[i][j])
            Table_Body_HTML = Table_Body_HTML  + '\n</tr>\n'
            j=j-1
        
        Table_HTML = Table_Heading_HTML + Table_Body_HTML +   "\n</table><BR><BR>\n\n"
        Alert = self.HTML_Header + "\n<body>\n\n" + Table_HTML + "\n</body>\n</HTML><BR><BR>"        
        Email_Subject = clientname + " - Sensor Alert"
        M.send_mail_html(Email_Subject,str(Alert))
        
        
        



	
