import requests
import json
import time
import os
import logging
import sys

logging.basicConfig(level=logging.INFO, filename ='progress.log')


QSKEY = "" 

def download_file(url,expected_size,output_path):
    expected_size = int(expected_size)
    print("Downloading File...")
    headers = {
            "content-type":"application/json; charset=UTF-8",
            "cookie":"",
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
            "x-client-data": "",
            "x-goog-authuser":"1"
    }    
    response = requests.get(url,headers=headers, stream = True)

    out_file = open(output_path,"wb")
    downloaded_amount = 0
    # This may be a bad idea for chunk size, but idk
    for chunk in response.iter_content(chunk_size=2**26):
        out_file.write(chunk)
        downloaded_amount+=len(chunk)
        sys.stdout.write("\r Progress: %d / %d" % (downloaded_amount,expected_size))
        sys.stdout.flush()
    out_file.close()
    print("\nDone!")
    return True

def get_job_status(job_id):
    exp_info = {
        "done":False,
        "archives":{}
    }
    
    
    url = f"https://takeout-pa.clients6.google.com/v1/exports/{job_id}?key={QSKEY}"

    headers = {
            "content-type":"application/json; charset=UTF-8",
            "cookie":"",
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
            "x-client-data": "",
            "x-goog-authuser":"1"
        }
        
    r= requests.get(url,headers=headers)
    if(r.status_code == 200):
        rdata = r.json()
        pdone = rdata.get('percentDone',0)
        sys.stdout.write("\rExport Progress: %d" % pdone)
        sys.stdout.flush()
        if(pdone == 100):
            export_status = rdata['exportJob']['status']
            if(export_status == "SUCCEEDED"):
                print("\nExport Done!")
                exp_info['done'] = True
                exp_info['archives'] = rdata['exportJob']['archives']
                return True,exp_info
            else:
                print("\nExport Failed!")
                print(r.json())
                return False,exp_info
        else:            
            return True,exp_info
    else:
        print(r.content())
        return False, exp_info
    

def export_items(item_ids):
    url = f"https://takeout-pa.clients6.google.com/v1/exports?key={QSKEY}" 

    headers = {
        "content-type":"application/json; charset=UTF-8",
        "cookie":"",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "x-client-data": "",
        "x-goog-authuser":"1"
    }

    payload = {
        "archiveFormat":None,
        "archivePrefix":"exported_",
        "conversions":None,
        "items":[],
        "locale":None
    }

    for iid in item_ids:
        payload['items'].append({"id":iid})

    r = requests.post(url,headers=headers,data=json.dumps(payload))

    if(r.status_code == 200):
        rdata = r.json()
        job_id = rdata['exportJob']['id']
        print("OK! Job ID: %s" % job_id)
        return True,job_id
    else:
        print(r.json())
        return False, ""

def do_export_job(job_info,incoming_path):
    output_paths = []
    status,job_id = export_items(job_info.keys())
    if(status == True):
        while 1:
            status,exp_info = get_job_status(job_id)
            if(status == False):
                print("Export Error!")
                break
            else:
                if(exp_info['done'] == True):
                    print("Archives to Pull")
                    print(exp_info['archives'])
                    for ar in exp_info['archives']:
                        filename = ar['fileName']                        
                        file_url = ar['storagePath']
                        size_comp = ar['compressedSize']
                        size_uncomp = ar['sizeOfContents']
                        print(f"Downloading: {filename} {size_comp} Bytes. [Real Size] {size_uncomp} Bytes...")
                        output_path = os.path.join(incoming_path,filename)
                        status = download_file(file_url,size_comp,output_path)
                        if(status == False):
                            return False,[]
                        output_paths.append(output_path)
                    if(status == True):
                        return True,output_paths
            time.sleep(5)    
    return False,[]