"""
This utility migrates all archives in a given directory via takeout/export, 
unpacks them, and copies them to another location.
"""
import logging
import sys
logging.basicConfig(level=logging.INFO, filename ='progress.log')
import os
import takeout_export
import archive_unpacker
INCOMING_ROOT = "./incoming"


JOB_LST = [
{
"1VG4sCbUXwfPzTDAqesXcz3K4tZxv7I48":"2006 - B.part3.rar",
"1KahelcBPBJ46qnpl6I9W_aVoatNbmCHK":"2006 - B.part2.rar",
"1YXHErQURjvF0whZMfMx_pLGxW8KEXFJR":"2006 - B.part1.rar",
},{
"1MlF-EY7-n7cpeBHjh40FGmVtX67aMsqM":"2006 - A.part2.rar",
"1mUZF1GzvBQ2E_ZtF6p-jN5r9QUv1iZA4":"2006 - A.part1.rar",
},{
"1cDUD7Iw7uTjq4N56W-BGoxxkBW9xJog4":"2006 - #.rar",
}
]


def usage():
    print(f"Usage: {sys.argv[0]} destination_path")
    sys.exit(-1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()
    
    destination_path = sys.argv[1]
    for job_info in JOB_LST:
        print(f"Processing Job: {job_info}...")
        archive_unpacker.wipe_down_working_dir(INCOMING_ROOT)
        status,item_path = takeout_export.do_export_job(job_info,INCOMING_ROOT)
        if status == False:
            print(f"Export Error: {job_info}")
            sys.exit(-1)
        # Process any Zips we Had
        archive_unpacker.process_zips(INCOMING_ROOT)            
        # Sanitize What we Got
        archive_unpacker.sanitize_names(INCOMING_ROOT)
        # If this is Multi-Part, extract part1
        # If not, Just Extract whatever is in there to the destination.
        status = archive_unpacker.process_rars(INCOMING_ROOT,destination_path,multipart= len(job_info.keys()) != 1)
        if status == False:
            print(f"Unpack Error: {job_info}")
            sys.exit(-1)
        print(f"Processed {job_info}")
        logging.info(f"Processed {job_info}")   

        
        
            

    