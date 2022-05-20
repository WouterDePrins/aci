# Python script to get IP, MAC & VLAN Encap from a given BD and ping against the IP
# Create by Wouter De Prins | wdeprins@cisco.com

from urllib import response
import subprocess, platform, pprint, json, requests

url = "http://x.x.x.x/"
username = ""
password = ""

def login():
	payload = json.dumps({
	  "aaaUser": {
	    "attributes": {
	      "name": username,
	      "pwd": password
	    }
	  }
	})

	headers = {
	  'Content-Type': 'application/json',
	}

	api_url = "api/aaaLogin.json?"
	response = requests.request("POST", url + api_url, headers=headers, data=payload)
	cookie = json.loads(response.text)
	headers = {
	  'Content-Type': 'application/json',
	  'Cookie': 'APIC-cookie=' + cookie['imdata'][0]['aaaLogin']['attributes']['token']
	}
	return headers


def ping(host):
    ping_str = "-n 1" if  platform.system().lower()=="windows" else "-c 1"
    args = "ping " + " " + ping_str + " " + host
    need_sh = False if  platform.system().lower()=="windows" else True

    return subprocess.call(args, shell=need_sh) == 0

def ping_ip_in_bd(tn, bd):
	api_url = "api/node/class/fvCEp.json?query-target-filter=and(not(wcard(fvCEp.dn,\"__ui_\")),eq(fvCEp.bdDn,\"uni/tn-{}/BD-{}\"))&rsp-subtree=children&rsp-subtree-class=fvIp&order-by=fvCEp.mac|desc".format(tn, bd)
	ip_list = []
	response = requests.request("GET", url + api_url, headers=login())
	response_json = json.loads(response.text)
	for i in response_json["imdata"]:
			info = {}
			info["mac"] = i["fvCEp"]["attributes"]["mac"]
			info['vlan_encap'] = i["fvCEp"]["attributes"]["encap"]			
			if "children" in i["fvCEp"]:
				info["ip"] = i["fvCEp"]["children"][0]["fvIp"]["attributes"]["addr"]
			ip_list.append(info)

	pp = pprint.PrettyPrinter(indent=4)
	print("Below you can find the endpoints from bridge domain {} in tenant {}: \n".format(bd, tn))
	pp.pprint(ip_list)

	for j in ip_list:
		if 'ip' in j:
			ping(j['ip'])
		

# execute function | arg are Tenant and Bridge Domain
ping_ip_in_bd("ap", "bd")


