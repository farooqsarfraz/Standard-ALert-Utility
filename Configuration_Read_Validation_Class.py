import json
import pandas as pd
import xml.etree.ElementTree as e
import Connection_class
import os,re
from datetime import datetime
from importlib import reload 
reload(Connection_class)
import sys
                
class Configration_Read_Validation():
    
    '''
    A Class created to compute the mismatches between runtime variables 
    and SME joined information against these variables.
    Input : Parameters (String containing the columns names)
    Output : Flag (True/False) , Status (), HTML String
    '''
    
    config_dict = dict()
    Table_Notation = dict()
    Connections=dict()
    EngineID_Prod = ''
    Last_NDays= ''
    AI_SME_Table = ''
    Conn = Connection_class.Connections()
    #M = mailer_class.Mailer()
    
    def __init__(self):
        pass
        return None
    
    def CreateDirectories(self,Folder):
    
        Return_Arg = ''
    
        try:
            if not os.path.exists(Folder):
                os.makedirs(Folder)
            #Return_Arg.append(Path)

        except Exception as e:
            Return_Arg = " Exception in createDirectories - " + str(e)
        
        return True , Return_Arg

    def FileMaskDelete(self, Directory, FileMask):
    
        try:
            for file in os.listdir(Directory):
                if re.search(FileMask, file):
                    os.remove(os.path.join(Directory, file))
                
        except Exception as e:
            return False, " Exception in FileMaskDelete - " + str(e)
        return True , ""  
    
    def Read_Configuration(self , FileName):
        
        '''
        Module parsing the given json config file to read the Mysql different connection credentials 
        and lookup tables information.
        '''
        print("Reading Configuration ... ")
        if not os.path.isfile(os.getcwd()+"\\"+FileName):
            return False , FileName +' file does not exist at ' +os.getcwd() + '\\'
        
        JsonFile = open(FileName).read()
        
        try:
            self.config_dict = json.loads(JsonFile)
        except ValueError as e:
            print( FileName +': Decoding JSON has failed \nInformation: ' + str(e) )
            sys.exit(0)
        print("Done.")
        print("Validating Configuration ... ")
        Status , Return_Arg = self.Validate_JSONConfig()
        if not Status:
            return Status , Return_Arg
        print("Done.")
    
        return True , ''  
    
    
    def Validate_JSONConfig(self):
        
        ###### DB Config Validation #####
        arch = self.Conn.mysql_conn(**self.config_dict['DBCredentials']['arch'])
        if not (arch):
             return False , "Archival Mysql Credentials are not correct in JSON Configration\n"
        arch.close()
        prod = self.Conn.mysql_conn(**self.config_dict['DBCredentials']['prod'])
        if not (prod ):
             return False , "Production Mysql Credentials are not correct in JSON Configration"
        prod.close()
        stg = self.Conn.mysql_conn(**self.config_dict['DBCredentials']['stg'])
        if not (stg ):
             return False , "Production Mysql Credentials are not correct in JSON Configration"
        stg.close()
        ai = self.Conn.mysql_conn(**self.config_dict['DBCredentials']['ai'])
        if not (ai ):
             return False , "AI Mysql Credentials are not correct in JSON Configration"
        ai.close()
                 
        ##### Email config Validation #####
        
        if self.config_dict['EmailInfo']['Email_To'] is None or self.config_dict['EmailInfo']['Email_To'] =="":
            return False , "ETL_Email_To cannot be empty in JSON Configration"
        
        if self.config_dict['EmailInfo']['Email_From'] is None or self.config_dict['EmailInfo']['Email_From'] =="":
            return False , "ETL_Email_From cannot be empty in JSON Configration"
        
        if self.config_dict['EmailInfo']['SMTP_HOST'] is None or self.config_dict['EmailInfo']['SMTP_HOST'] =="":
            return False , "SMTP_HOST cannot be empty in JSON Configration"
        
        ##### Client Details Validation ######
        
        if self.config_dict['ClientDetails']['Clientname'] is None or self.config_dict['ClientDetails']['Clientname'] =="":
            return False , "ClientDetails - ClientName cannot be empty in JSON Configration"
        
        if self.config_dict['ClientDetails']['programid'] is None or self.config_dict['ClientDetails']['programid'] =="":
            return False , "ClientDetails - programid cannot be empty in JSON Configration"
        
        if self.config_dict['ClientDetails']['Data_Lag'] is None or self.config_dict['ClientDetails']['Data_Lag'] =="":
            return False , "ClientDetails - Data_Lag cannot be empty in JSON Configration"
        
        if self.config_dict['ClientDetails']['Alert_Config_detail'][0] is None or self.config_dict['ClientDetails']['Alert_Config_detail'][0] =="":
            return False , "ClientDetails - Alert_Config_Server cannot be empty in JSON Configration"
        
        if self.config_dict['ClientDetails']['Alert_Config_detail'][1] is None or self.config_dict['ClientDetails']['Alert_Config_detail'][1] =="":
            return False , "ClientDetails - Alert_Config_DB cannot be empty in JSON Configration"
        
        if self.config_dict['ClientDetails']['Red_Blue_Status'] is None or self.config_dict['ClientDetails']['Red_Blue_Status'] =="":
            return False , "ClientDetails - Red_Blue_Status cannot be empty in JSON Configration"
        
        if self.config_dict['ClientDetails']['Red_Blue_Status'].lower() =="y" and self.config_dict['ClientDetails']['Team'] =="":
            return False , "ClientDetails - Team Name cannot be empty in JSON Configration"
             
        ###### Software config Validation ######
        
        if self.config_dict['SoftwareDetails']['ZipExePath'] is None or self.config_dict['SoftwareDetails']['ZipExePath'] =="":
            return False , "SoftwareDetails - ZipExePath cannot be empty in JSON Configration"
        
        
        ###### Lookup Table config Validation ######
        
        if self.config_dict['Lookup_Tables']['EngineID_Prod'] is None or self.config_dict['Lookup_Tables']['EngineID_Prod'] =="":
            return False , "EngineID_Prod - cannot be empty in JSON Configration"
        
        if self.config_dict['Lookup_Tables']['AI_Callguid_Column_Name'] is None or self.config_dict['Lookup_Tables']['AI_Callguid_Column_Name'] =="":
            return False , "AI_Callguid_Column_Name - Name cannot be empty in JSON Configration"
        
        if self.config_dict['Lookup_Tables']['AI_SME_Table'] is None or self.config_dict['Lookup_Tables']['AI_SME_Table'] =="":
            return False , "AI_SME_Table - Name cannot be empty in JSON Configration"
        
        if str(self.config_dict['Lookup_Tables']['Last_NDays']) is None or str(self.config_dict['Lookup_Tables']['Last_NDays']) =="":
            return False , "Last_NDays - cannot be empty in JSON Configration"

        
        self.EngineID_Prod=self.config_dict['Lookup_Tables']['EngineID_Prod']
        self.Last_NDays = str(self.config_dict['Lookup_Tables']['Last_NDays'])
        self.AI_Callguid = self.config_dict['Lookup_Tables']['AI_Callguid_Column_Name']
        self.AI_SME_Table = self.config_dict['Lookup_Tables']['AI_SME_Table']
        
        Table_Notation     =   self.config_dict['Lookup_Tables']['Table_Notation']
        for k in Table_Notation.keys():
            if type(Table_Notation[k]) is list:
                self.Table_Notation[k.lower()]=  [j.lower() for j in Table_Notation[k]]
            else:
                self.Table_Notation[k] = Table_Notation[k].lower()
        #print(self.Table_Notation)
        return True, ""
    
    def Create_Connection (self, Server):
        self.Connections[Server]= self.Conn.mysql_conn(**self.config_dict['DBCredentials'][Server])
        
    def Close_Connection (self, Server):
        self.Connections[Server].close()   
 
         