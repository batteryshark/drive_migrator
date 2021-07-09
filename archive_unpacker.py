import os,tempfile,shutil,re
from pyunpack import Archive

def unpack_to_tmpdir(in_file):
    outd = tempfile.TemporaryDirectory()
    print(f"Extracting {in_file} to {outd.name}...")
    Archive(in_file).extractall(outd.name)
    print("Done!")
    
      
def remove_file(in_file):
    os.remove(in_file)
    
def sanitize_names(in_path):
    for root,dirs,files in os.walk(in_path):
        for f in files:
            fpath = os.path.join(root,f)
            fpath_new = re.sub(r'-\d\d\d.rar',r'.rar',fpath)    
            shutil.move(fpath,fpath_new)
        break            


def wipe_down_working_dir(in_path):
    for root,dirs,files in os.walk(in_path):
        for f in files:
            fpath = os.path.join(root,f)
            if(fpath.endswith("zip") or fpath.endswith("rar")):                
                os.remove(fpath)    
        break

def process_zips(in_path):
    for root,dirs,files in os.walk(in_path):
        for f in files:
            fpath = os.path.join(root,f)
            if(fpath.endswith("zip")):
                unpack_to(fpath,in_path) 
        break

def process_rars(in_path,out_path,multipart=False):
    status = False
    for root,dirs,files in os.walk(in_path):
        for f in files:
            fpath = os.path.join(root,f)
            if(fpath.endswith("rar")):
                if(multipart == True):
                    if(".part1" in fpath):
                        status = unpack_to(fpath,out_path)
                else:
                    status = unpack_to(fpath,out_path)
        break
    return status

def handle_nested(in_path,out_path):
    with tempfile.TemporaryDirectory() as outd:
        status = unpack_to(in_path,outd,nested=True)
        if(status == False):
            return False

        for root,dirs,files in os.walk(outd):
            for f in files:
                if(f.endswith("rar")):
                    fpath = os.path.join(root,f)
                    status = unpack_to(fpath,out_path)
            break                    
        return status                
    return False

def unpack_to(in_path, out_path,nested=False):      
    try:
        print(f"Extracting {in_path} to {out_path}...")
        Archive(in_path).extractall(out_path)
        print("Done!")
        return True
    except Exception as e:
        print("Extract Error!")
        print(e)
        return False
    return False