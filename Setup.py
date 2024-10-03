import pip,time

#List of libraries and modules to be installed
Modules=['pygame','numpy']

def downloadIfNeeded(module):
    try:
        print("------------------------------------------------------")
        print("Checking for",str(module))
        __import__(str(module))
        print(str(module),"already exists :)")
    except:
        print(str(module),"not found !!!")
        time.sleep(0.25)
        print("Attempting to install",str(module)+"...")
        try:
            pip.main(['install',str(module)])
            print(str(module),"installed succesfully :)")
        except Exception as e:
            print("ERR: Failed to install",str(module),"!!!")
            print(e)
        

for Module in Modules:
    downloadIfNeeded(Module)

time.sleep(2)
