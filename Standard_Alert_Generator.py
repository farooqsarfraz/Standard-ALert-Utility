import Alert_class
import sys
from importlib import reload 
		

reload(Alert_class)


def main():
    
    ErrorMessage=""
    if len(sys.argv) == 2:
        A = Alert_class.Alerts()
        A.Complete_Alert(sys.argv[1])
        #Message="Success : Alert is generated ! "
        #print(Message)
        
    elif len(sys.argv) == 1:
        ErrorMessage="Error : Alert Name is missing ! "
        print(ErrorMessage)
        
    else:
        ErrorMessage="Error : Incorrect Numbers of parameters ! \n (Required number of parameters (1) = Alert Name) "
        print(ErrorMessage)
    
         
if __name__ == "__main__":
    
    main()
#    config = {"Alert"           : "ASA alert",
#              "FolderPath"      : "E:\\Saqib\\Generic Alert\\Skill_wise_ASA_Alert\\",
#              "Email_To"        : "afiniti.etl.sagajobs@afiniti.com",
#              "Email_CC"        : "",
#              "Email_Subject"   : "SAGA Jobs | Agent and Caller Wait Time Alert_With_Threshold | Test1234",
#              "Ordered"         : "1",
#              "Custom_Checks"   : """Agent Wait Time : MaxWait_On : MaxWait_Off : >2 : 2 : Default |
#                                      Agent Wait Time : Avg_Wait_On : Avg_Wait_Off : >1.2 : 2 : Default |
#                                      Skill_Wise_ASA_Alert : MaxWait_On : MaxWait_Off : >2 : 2 : Default |
#                                      Skill_Wise_ASA_Alert : OnASA : OffASA : >1.2 : 2 : Default"""
#             }
#    config = {"Alert"           : "Gain alert 11",
#              "FolderPath"      : "E:\\Saqib\\Generic Alert\\gain_alert\\",
#              "Email_To"        : "afiniti.etl.sagajobs@afiniti.com",
#              "Email_CC"        : "saqib.ishtiaq@afiniti.com",
#              "Email_Subject"   : "SAGA | Gain Alert ETL | Test234",
#              "Ordered"         : "1",
#              "Custom_Checks"   : """"""
#             }     


    #A = Alerts()

    #A.Complete_Alert("",**config)
    #A.Complete_Alert("Negative Sales")
    
    #A.Complete_Alert("",**config)
    
    #A.Complete_Alert("VI Agent alert")
    
    
      # Get the current working directory (cwd)
    
    #files = os.listdir(cwd)  # Get all the files in that directory
    #print("Files in '%s': %s" % (cwd, files))
    