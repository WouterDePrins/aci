# This script allows you to create a new EPG in a give application profile in a given Tenant. This is useful when deploying a new EPG in a Kubernetes tenant in ACI. The newly created EPG will inherit the contract of the 'kube-pod-bd' EPG so you don't need to re-create this. Created by Wouter De Prins - SE @ Cisco #

import json
import requests

###### Fill in below parameters ######

username = '' #APIC Username
password = '' #APIC Password
epg = '' #New EPG Name
tenant = '' #Kubernetes Tenant
ap = '' #AP where you want this new EPG to be deployed
baseUrl = "http://X.X.X.X/" #IP address of the APIC
k8s_dom = "" #Kubernetes Domain name

######################################

def login():
  payload = {
    "aaaUser": {
      "attributes": 
        {
            "name" : username,
            "pwd" : password 
        }
    }
  }

  login = baseUrl + "api/aaaLogin.json"
	request = requests.request("POST", login, json = payload)
	pretty = json.loads(request.text)
	return pretty['imdata'][0]['aaaLogin']['attributes']['token']

def header():
	token = login()
	headers = {
 	 'Cookie': 'APIC-cookie=' + token
	}
	return headers
}

def createEpg():
	url = baseUrl + "api/node/mo/uni/tn-" + tenant + "/ap-" + ap + "/epg-" + epg + ".json"
	payload =  {
	  "fvAEPg": {
	    "attributes": {
	      "dn": "uni/tn-" + tenant + "/ap-" + ap + "/epg-" + epg,
	      "name": epg,
	      "rn": "epg-" + epg,
	      "status": "created"
	    },
	    "children": [
	      {
	        "fvRsBd": {
	          "attributes": {
	            "tnFvBDName": "kube-pod-bd",
	            "status": "created,modified"
	          },
	          "children": []
	        }
	      },
	      {
	        "fvRsSecInherited": {
	          "attributes": {
	            "tDn": "uni/tn-" + tenant + "/ap-" + ap + "/epg-kube-default",
	            "status": "created"
	          },
	          "children": []
	        }
	      },
	      {
	        "fvRsDomAtt": {
	          "attributes": {
	            "resImedcy": "immediate",
	            "tDn": "uni/vmmp-Kubernetes/dom-" + k8s_dom,
	            "status": "created"
	          },
	          "children": [
	            {
	              "vmmSecP": {
	                "attributes": {
	                  "status": "created"
	                },
	                "children": []
	              }
	            }
	          ]
	        }
	      }
	    ]
	  }
	}
	response = requests.request("POST", url, json=payload, headers = header(), verify=False)
