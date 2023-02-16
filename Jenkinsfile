// @Library('stratusjenkins-sharedlibrary@feature/customemailtemplate') _
@Library('stratus-sharedlibrary@chje') _
import com.albertsons.stratus.jenkins.MsgLogger

env.AUTOTRIGGERED = true
env.USE_CUSTOM_EMAIL_TEMPLATE = 'true'

def initialize_environment_config(){
	
	//read yaml config file and set the required parameters for environment
	def envConfig = readYaml file: 'config/env-config.yaml'	
	def pcfenvconfig = envConfig.pcf.foundations["${USER_ENV_NAME}"]
	env.APPSMAN_URL = pcfenvconfig.appsman_url
	env.APPSMAN_CRED_ID = pcfenvconfig.cf_cred_id
	env.LOG_CRED_ID = pcfenvconfig.log_cred_id
	
	withCredentials([usernamePassword(credentialsId: "${env.LOG_CRED_ID}", passwordVariable: 'PCF_PASS', usernameVariable: 'PCF_USER')]) {				
		env.log_analytics_workspace_id  = "${PCF_USER}"
		env.log_analytics_workspace_secret  = "${PCF_PASS}"
	}

	withCredentials([usernamePassword(credentialsId: "stratusjenkins-cf-log-common-user", passwordVariable: 'PCF_PASS', usernameVariable: 'PCF_USER')]) {				
		env.log_analytics_common_workspace_id  = "${PCF_USER}"
		env.log_analytics_common_workspace_secret  = "${PCF_PASS}"
	}		
}

def build_logger_payload_json(itemcount,total_records,binding){
      
		def dataContent = ""
		def textContent = """\
		{
          "month": ${binding.month},
          "year": ${binding.year},
          "average_app_instances": ${binding.average_app_instances},
          "maximum_app_instances": ${binding.maximum_app_instances},
          "app_instance_hours": ${binding.app_instance_hours}		  
		}""".stripIndent()

        if(itemcount == 1){
            //Write Header
            writeFile(
              file: "${payloadfile}",
              text: "["  + "\n"
            )
        }

        //Escape comma for last item
  			if(itemcount == total_records){
    			dataContent = textContent + "\n"
  			}
  			else{
  				 dataContent = textContent + ",\n"
  			}

        //Write data
    		def readContent = readFile "${payloadfile}"
    		writeFile(
    			file: "${payloadfile}",
    			text: readContent + dataContent
    		)

        if(itemcount == total_records){
              //Write Footer
              readContent = readFile "${payloadfile}"
          		writeFile(
          			file: "${payloadfile}",
          			text: readContent + "]"
          		)
        }
}

def post_logs_to_log_analytics(){						
		//Install Python & Requests Library
		def packageinstalled = sh(script:'which python || date', returnStdout:true).trim()		
		if (packageinstalled != "/usr/bin/python"){
			echo "Package Installing..."
			sh """
				sudo apt-get update -y
				sudo apt-get install -y python-requests
			"""
		}
		else{
			echo "Package Already Installed..."
		}
		
		echo "Started Posting the Request to Log Analytics..."	
		def Post_Return_Code = sh(script:'python3 scripts/post-logs-to-log-analytics.py', returnStdout:true).trim()
		if (Post_Return_Code == "Accepted"){	
			echo "Success : Posting the Request to Log Analytics..."		
		}
		else 
		{
			echo "Failure : Posting the Request to Log Analytics..."	
			currentBuild.result = 'FAILURE'
		}
	
}

def generate_instance_usage_report() {			
	
	//Write data
	sh """		
	    	
		echo '*****************************************************************************' | sudo tee $filename
		echo '*****************************************************************************' | sudo tee -a $filename
		echo '                          PCF Instance Usage Report                          ' | sudo tee -a $filename
		echo '*****************************************************************************' | sudo tee -a $filename
		echo '*****************************************************************************' | sudo tee -a $filename
		echo ' Date              : $Todays_Date' | sudo tee -a $filename
		echo ' ENV               : $USER_ENV_NAME' | sudo tee -a $filename		
		echo '*****************************************************************************' | sudo tee -a $filename	

		wget https://github.com/alexvasseur/cf_get_events/releases/download/2.6.0/bcr-plugin-linux
		cf install-plugin -f ./bcr-plugin-linux
		cf bcr --monthly --ai --si | sudo tee -a $filename  
		 		
		echo '*****************************************************************************' | sudo tee -a $filename    
		echo '*                                 END OF REPORT                              ' | sudo tee -a $filename
		echo '*****************************************************************************' | sudo tee -a $filename
		
		
		#apply retention file and keep 365 days						
		sudo find /mnt/isharesafeway/reports/pcf-instance-usage-report/${USER_ENV_NAME}/ -type d -name '*-*-*-*-*-*' -mtime +365 -print0 | xargs -0 -I {} rm -rf {} \\;
		
		#move file to storage account
		sudo mkdir -p /mnt/isharesafeway/reports/pcf-instance-usage-report/${USER_ENV_NAME}/$Todays_Date 
		sudo cp $filename /mnt/isharesafeway/reports/pcf-instance-usage-report/${USER_ENV_NAME}/$Todays_Date/
		sudo cp $outputfile /mnt/isharesafeway/reports/pcf-instance-usage-report/${USER_ENV_NAME}/$Todays_Date/
		sudo cp $payloadfile /mnt/isharesafeway/reports/pcf-instance-usage-report/${USER_ENV_NAME}/$Todays_Date/
	"""	
}

def get_combined_instance_usage_details() {
	env.payloadfile="${USER_ENV_NAME}" + "-instance-usage-payload-" + "${Todays_Date}" + ".json"

	
	dir("instance-usage-report/$USER_ENV_NAME"){			
		withEnv(["HOME=${workspace}/instance-usage-report/${USER_ENV_NAME}"]) {						
			
			def SUB_ENV = "np-west"
			def NPWEST_INSTANCE_OBJ = readJSON file: "../${SUB_ENV}/${SUB_ENV}-instance-usage-output-${Todays_Date}.json"					
			def NPWEST_INSTANCE_MONTHLY_REPORT = NPWEST_INSTANCE_OBJ.monthly_reports					
			def npwest_count = NPWEST_INSTANCE_MONTHLY_REPORT.size() - 1
			//echo "${npwest_count}"
			
			
			SUB_ENV = "pd-west"
			def PDWEST_INSTANCE_OBJ = readJSON file: "../${SUB_ENV}/${SUB_ENV}-instance-usage-output-${Todays_Date}.json"						
			def PDWEST_INSTANCE_MONTHLY_REPORT = PDWEST_INSTANCE_OBJ.monthly_reports		
			def pdwest_count = PDWEST_INSTANCE_OBJ.monthly_reports.size() - 1
			//echo "${pdwest_count}"			
			
			SUB_ENV = "pd-east"
			def PDEAST_INSTANCE_OBJ = readJSON file: "../${SUB_ENV}/${SUB_ENV}-instance-usage-output-${Todays_Date}.json"					
			def PDEAST_INSTANCE_MONTHLY_REPORT = PDEAST_INSTANCE_OBJ.monthly_reports					
			def pdeast_count = PDEAST_INSTANCE_MONTHLY_REPORT.size() - 1
			//echo "${pdeast_count}"		
			
			SUB_ENV = "np-east"
			def NPEAST_INSTANCE_OBJ = readJSON file: "../${SUB_ENV}/${SUB_ENV}-instance-usage-output-${Todays_Date}.json"					
			def NPEAST_INSTANCE_MONTHLY_REPORT = NPEAST_INSTANCE_OBJ.monthly_reports			
			def npeast_count = NPEAST_INSTANCE_MONTHLY_REPORT.size() - 1
			//echo "${npeast_count}"
					
			
			def month = 0
			def year = 0
			def average_app_instances = 0 
			def maximum_app_instances = 0
			
			def binding = [:]
			def total_records = 30
			for(index = 0; index < total_records; index++){				
				def combined_month = 0
				def combined_year = 0
				def combined_average_app_instances = 0 
				def combined_maximum_app_instances = 0
				def combined_app_instance_hours = 0
				if(npwest_count > 0){
					month = NPWEST_INSTANCE_MONTHLY_REPORT[npwest_count].month
					year = NPWEST_INSTANCE_MONTHLY_REPORT[npwest_count].year
					average_app_instances = NPWEST_INSTANCE_MONTHLY_REPORT[npwest_count].average_app_instances.toInteger()
					maximum_app_instances = NPWEST_INSTANCE_MONTHLY_REPORT[npwest_count].maximum_app_instances.toInteger()
					app_instance_hours = NPWEST_INSTANCE_MONTHLY_REPORT[npwest_count].app_instance_hours.toInteger()
					
					//echo "npwest ${month} ${year} ${average_app_instances} ${maximum_app_instances}"
					npwest_count = npwest_count - 1
					
					combined_month = month
					combined_year = year
					combined_average_app_instances = combined_average_app_instances + average_app_instances
					combined_maximum_app_instances = combined_maximum_app_instances + maximum_app_instances
					combined_app_instance_hours = combined_app_instance_hours + app_instance_hours
				}
				
				if(pdwest_count > 0){
					month = PDWEST_INSTANCE_MONTHLY_REPORT[pdwest_count].month
					year = PDWEST_INSTANCE_MONTHLY_REPORT[pdwest_count].year
					average_app_instances = PDWEST_INSTANCE_MONTHLY_REPORT[pdwest_count].average_app_instances.toInteger()
					maximum_app_instances = PDWEST_INSTANCE_MONTHLY_REPORT[pdwest_count].maximum_app_instances.toInteger()
					combined_app_instance_hours = PDWEST_INSTANCE_MONTHLY_REPORT[pdwest_count].app_instance_hours.toInteger()
					
					//echo "pdwest ${month} ${year} ${average_app_instances} ${maximum_app_instances}"
					pdwest_count = pdwest_count - 1
					combined_average_app_instances = combined_average_app_instances + average_app_instances
					combined_maximum_app_instances = combined_maximum_app_instances + maximum_app_instances	
					combined_app_instance_hours = combined_app_instance_hours + app_instance_hours					
				}
				if(pdeast_count > 0){
					month = PDEAST_INSTANCE_MONTHLY_REPORT[pdeast_count].month
					year = PDEAST_INSTANCE_MONTHLY_REPORT[pdeast_count].year
					average_app_instances = PDEAST_INSTANCE_MONTHLY_REPORT[pdeast_count].average_app_instances.toInteger()
					maximum_app_instances = PDEAST_INSTANCE_MONTHLY_REPORT[pdeast_count].maximum_app_instances.toInteger()
					combined_app_instance_hours = PDEAST_INSTANCE_MONTHLY_REPORT[pdeast_count].app_instance_hours.toInteger()
					
					//echo "pdeast ${month} ${year} ${average_app_instances} ${maximum_app_instances}"
					pdeast_count = pdeast_count - 1
					combined_average_app_instances = combined_average_app_instances + average_app_instances
					combined_maximum_app_instances = combined_maximum_app_instances + maximum_app_instances	
					combined_app_instance_hours = combined_app_instance_hours + app_instance_hours
				}				
				
				if(npeast_count > 0){
					month = NPEAST_INSTANCE_MONTHLY_REPORT[npeast_count].month
					year = NPEAST_INSTANCE_MONTHLY_REPORT[npeast_count].year
					average_app_instances = NPEAST_INSTANCE_MONTHLY_REPORT[npeast_count].average_app_instances.toInteger()
					maximum_app_instances = NPEAST_INSTANCE_MONTHLY_REPORT[npeast_count].maximum_app_instances.toInteger()
					combined_app_instance_hours = NPEAST_INSTANCE_MONTHLY_REPORT[npeast_count].app_instance_hours.toInteger()
					
					//echo "npeast ${month} ${year} ${average_app_instances} ${maximum_app_instances}"					
					npeast_count = npeast_count - 1
					combined_average_app_instances = combined_average_app_instances + average_app_instances
					combined_maximum_app_instances = combined_maximum_app_instances + maximum_app_instances
					combined_app_instance_hours = combined_app_instance_hours + app_instance_hours
				}

				//echo "Combined ${combined_month} ${combined_year} ${combined_average_app_instances} ${combined_maximum_app_instances}"
				
				binding = [
					month: combined_month,
					year: combined_year,
					average_app_instances: combined_average_app_instances,
					maximum_app_instances: combined_maximum_app_instances,
					app_instance_hours: combined_app_instance_hours					
				]			
				build_logger_payload_json(index+1,total_records,binding)				
			}
			
			//Move the file to storage account
			sh """
				sudo mkdir -p /mnt/isharesafeway/reports/pcf-instance-usage-report/${USER_ENV_NAME}/$Todays_Date
				sudo cp $payloadfile /mnt/isharesafeway/reports/pcf-instance-usage-report/${USER_ENV_NAME}/$Todays_Date/
			"""
		}
	}
	

	//Post the Logger Payload
	env.PAYLOAD_FILE_PATH = "instance-usage-report/${USER_ENV_NAME}/$payloadfile"
    env.WORKSPACE_ID = log_analytics_common_workspace_id
    env.WORKSPACE_KEY = log_analytics_common_workspace_secret
    env.CUSTOM_LOG_NAME = "CF_Instance_Usage_Details_${ENVIRONMENT}_CL"
	//env.ENVIRONMENT = USER_ENV_NAME
	post_logs_to_log_analytics()				
}

def get_instance_usage_details() {
	env.filename="${USER_ENV_NAME}" + "-instance-usage-report-" + "${Todays_Date}" + ".txt"
	env.outputfile="${USER_ENV_NAME}" + "-instance-usage-output-" + "${Todays_Date}" + ".json"
	env.payloadfile="${USER_ENV_NAME}" + "-instance-usage-payload-" + "${Todays_Date}" + ".json"

	initialize_environment_config()
	
	dir("instance-usage-report/$USER_ENV_NAME"){			
		withEnv(["HOME=${workspace}/instance-usage-report/${USER_ENV_NAME}"]) {		
			withCredentials([usernamePassword(credentialsId: "${APPSMAN_CRED_ID}", passwordVariable: 'PCF_PASS', usernameVariable: 'PCF_USER')]) {	
				env.APPSMAN_USER = "${PCF_USER}"
				env.APPSMAN_PASSCODE = "${PCF_PASS}"	
			
				//Login
				def LOGIN = sh(script:'cf login -a $APPSMAN_URL -u $APPSMAN_USER -p $APPSMAN_PASSCODE --skip-ssl-validation', returnStdout:true)	
			}
							
			env.APP_USAGE_ENDPOINT = APPSMAN_URL.replace("https://api.", "https://app-usage.")
			def INSTANCE_LIST = sh(script:'curl $APP_USAGE_ENDPOINT/system_report/app_usages -k -v -H "authorization: `cf oauth-token`"', returnStdout:true)			
			def INSTANCE_OBJ = readJSON text: INSTANCE_LIST					
			def INSTANCE_REPORT_DATE = INSTANCE_OBJ.report_time
			def INSTANCE_MONTHLY_REPORT = INSTANCE_OBJ.monthly_reports
			def INSTANCE_YEARLY_REPORT = INSTANCE_OBJ.yearly_reports
			def INSTANCE_OUTPUT = INSTANCE_LIST
			
			writeJSON file: "${outputfile}", json: INSTANCE_OBJ
			writeJSON file: "${payloadfile}", json: INSTANCE_OBJ.monthly_reports
			
			generate_instance_usage_report()
		}
	}
	//Post the Logger Payload to common reports LAWS
	env.PAYLOAD_FILE_PATH = "instance-usage-report/${USER_ENV_NAME}/$payloadfile"	
    env.WORKSPACE_ID = log_analytics_common_workspace_id
    env.WORKSPACE_KEY = log_analytics_common_workspace_secret 
    env.CUSTOM_LOG_NAME = "CF_Instance_Usage_Details_${ENVIRONMENT}_CL"
	//env.ENVIRONMENT = USER_ENV_NAME
	post_logs_to_log_analytics()	
	
	//Post the Logger Payload to environment specific LAWS
//	 env.PAYLOAD_FILE_PATH = "instance-usage-report/${USER_ENV_NAME}/$payloadfile"	
//   env.WORKSPACE_ID = log_analytics_workspace_id
//   env.WORKSPACE_KEY = log_analytics_workspace_secret
//   env.CUSTOM_LOG_NAME = "CF_Instance_Usage_Details_CL"
//	 env.ENVIRONMENT = USER_ENV_NAME
//	post_logs_to_log_analytics()				
}
	
node('Jenkins_Agent1') {
	
	properties([
		pipelineTriggers([cron('''
        	0 3 * * *
    ''')])
])
	stage('checkout stage') {
		checkout scm
	}

	stage('prepare-environment') {
        try {	
		
			def date = new Date()
			env.Todays_Date = date.format("yyyy-MM-dd-HH-mm-ss", TimeZone.getTimeZone('UTC'))
			
			def packageinstalled = sh(script:'cf plugins | grep bcr || date', returnStdout:true).trim()
		
		if (packageinstalled != "bcr"){
			echo "Package Installing..."
			sh """
				wget https://github.com/alexvasseur/cf_get_events/releases/download/2.6.0/bcr-plugin-linux
				cf install-plugin -f ./bcr-plugin-linux
			"""
		}
		else{
			echo "Package Already Installed..."
		}
		
        } catch(com.jcraft.jsch.JSchException e) {
            MsgLogger.error([
                category: 'prepare-environment',
                details: "ERROR: prepare-environment  in ${JOB_OPTION}"
            ],this)
        }
    }

    stage('sb-west-get-instance-usage-report') {
        try {				
			env.USER_ENV_NAME = "sb-west"
			env.ENVIRONMENT = "sbwest"
			//Generate Instance Usage Report	
			get_instance_usage_details();			
				
        } catch(com.jcraft.jsch.JSchException e) {
            MsgLogger.error([
                category: 'sandbox-get-instance-usage-report',
                details: "ERROR: get-instance-usage-report  in ${JOB_OPTION}"
            ],this)
        }
    }		
	
    stage('np-west-get-instance-usage-report') {
        try {	
			env.USER_ENV_NAME = "np-west"
			env.ENVIRONMENT = "npwest"
			//Generate Instance Usage Report	
			get_instance_usage_details();
		
        } catch(com.jcraft.jsch.JSchException e) {
            MsgLogger.error([
                category: 'nonprod-get-instance-usage-report',
                details: "ERROR: get-instance-usage-report  in ${JOB_OPTION}"
            ],this)
        }
    }
	
    stage('pd-west-get-instance-usage-report') {
        try {	
			env.USER_ENV_NAME = "pd-west"
			env.ENVIRONMENT = "pdwest"
			//Generate Instance Usage Report	
			get_instance_usage_details();
						
        } catch(com.jcraft.jsch.JSchException e) {
            MsgLogger.error([
                category: 'prod-get-instance-usage-report',
                details: "ERROR: get-instance-usage-report  in ${JOB_OPTION}"
            ],this)
        }
    }
	
    stage('np-east-get-instance-usage-report') {
        try {	
			env.USER_ENV_NAME = "np-east"
			env.ENVIRONMENT = "npeast"
			//Generate Instance Usage Report	
			get_instance_usage_details();
			
        } catch(com.jcraft.jsch.JSchException e) {
            MsgLogger.error([
                category: 'nonprod-east-get-instance-usage-report',
                details: "ERROR: get-instance-usage-report  in ${JOB_OPTION}"
            ],this)
        }
    }	
	
    stage('pd-east-get-instance-usage-report') {
        try {	
			env.USER_ENV_NAME = "pd-east"
			env.ENVIRONMENT = "pdeast"
			//Generate Instance Usage Report	
			get_instance_usage_details();
			
        } catch(com.jcraft.jsch.JSchException e) {
            MsgLogger.error([
                category: 'prod-east-get-instance-usage-report',
                details: "ERROR: get-instance-usage-report  in ${JOB_OPTION}"
            ],this)
        }
    }
	
    stage('combined-get-instance-usage-report') {
        try {	
			env.USER_ENV_NAME = "combined"
			env.ENVIRONMENT = "combined"
			//Generate Instance Usage Report	
			get_combined_instance_usage_details();
			
        } catch(com.jcraft.jsch.JSchException e) {
            MsgLogger.error([
                category: 'combined-get-instance-usage-report',
                details: "ERROR: get-instance-usage-report  in ${JOB_OPTION}"
            ],this)
        }
    }
   /*
    addStage('sb-east-get-instance-usage-report','any:any') {
        try {				
			env.USER_ENV_NAME = "sb-east"
			env.ENVIRONMENT = "sbeast"
			//Generate Instance Usage Report	
			get_instance_usage_details();			
				
        } catch(com.jcraft.jsch.JSchException e) {
            MsgLogger.error([
                category: 'sandbox-get-instance-usage-report',
                details: "ERROR: get-instance-usage-report  in ${JOB_OPTION}"
            ],this)
        }
    }*/	
	
}
