import pymysql as mc
#import mysql.connector as mc
#import sys

class Connections():
    def __init__(self,**kwargs):
        self.vars = {}
        if bool(kwargs) is True:
            self.refresh_vars(**kwargs)
        return None
    
    def refresh_vars(self,**kwargs):
        if bool(kwargs) is True:
            for key, value in kwargs.items():
                self.vars[key] = value
        return None        
    
    def mysql_conn(self,**kwargs):
        #print(kwargs)
        self.refresh_vars(**kwargs)
        try:
            connection = mc.connect(user=self.vars['user'],
                                password=self.vars['passwd'],
                                host=self.vars['host'],
                                port=self.vars['port'],
                                database=self.vars['db'],
                                local_infile=True)
        except mc.Error as e:
            self.Print_Msg(e)
            return False  
        
        return connection
		
    def mysql_StagingDB(self,**kwargs):
        self.refresh_vars(**kwargs)
        try:
            connection = mc.connect(user=self.vars['user'],
									password=self.vars['passwd'],
									host=self.vars['host'],
									port=self.vars['port'],
									database=self.vars['db_stg'],
                           local_infile=True)
        except mc.Error as e:
            self.Print_Msg(e)
		
        return connection
    
    def mysql_BtnHistoryDB(self,**kwargs):
        self.refresh_vars(**kwargs)
        try:
            connection = mc.connect(user=self.vars['user'],
									password=self.vars['passwd'],
									host=self.vars['host'],
									port=self.vars['port'],
									database=self.vars['db_btnh'])

        except mc.Error as e:
            self.Print_Msg(e)
        
        return connection
		
    def Print_Msg(self,e):
        Message=""
        #Message = "Error code: "+ str(e.errno)  + "\n" # error number
       # Message = Message + "SQLSTATE value: "+ str(e.sqlstate) +"\n"  # SQLSTATE value
        #Message = Message + "Error message:", str(e.msg) +"\n"         # error message
        Message = Message + "Error:", str(e)  +"\n"                    # errno, sqlstate, msg values
        print(Message)
        
        #return Message
		