from django.shortcuts import render
from django.http import JsonResponse
from subprocess import Popen, PIPE
#from django.views.decorators.csrf import csrf_exempt
import psutil



#dict of running processes
#{KEYS: pids,  VALUES: process objects}
procs = {}   

#dict of scripts (in services folder)
#{KEYS: simplified script name, VALUES: actual script (string)}
scripts = {"tor": "exec screen -D -m -S tor tor", "gotty": "exec gotty -w --port ${PORT:-8090} screen -r -d tor" } 





"""NOTES:
        - Downloaded Go v1.10
        - Downloaded gotty
        - 'exec' required to keep shell (opened by Popen()) open
        - When starting process with 'screen', use -D to keep it attached and able to be
            discovered by python
        - You have to first create an env and then set the path to use gotty 
            (-->  $GOBIN/gotty && export PATH="$PATH:$GOBIN" && source ~/.profile)
        
        - sudo netstat -plnt (check status of all ports)
        
TODO's:
        1. Properly rename 'webpage#' names to something more intuitive
        2. Create separate thread/process to monitor status of all processes
            and have a way to restart somethingthat has stopped
        3. Standardize everything so that we only have to add a txt file
            with the shell command(s)/scripts into a "services" folder
            andeverything else is taken care of
                i.e. adding myScript.txt to the 'services' folder will 
                automatically create a new button in the control hub
                that runs the script specified in myScripts.txt
        
"""





def androidprocessmanager(request):
    """return home page"""
    return render(request, "androidprocessmanager.html", {})




def startprocess(request):  
    """
        Start the target process, save its name/pid to a list, and return them as
        data
    """
        
    processName = request.POST.get("processName")       #get name of process/button pressed
    shellcmd = scripts[processName]                     #get corresponding script
    proc= Popen(shellcmd, stdout=PIPE, shell = True)    #start process
    procs[proc.pid] = proc                              #add to list of running processes
    
    
    data = {'pid': proc.pid, 'name': processName}       #package and send data
    return JsonResponse(data)
    
    




#@csrf_exempt
def stopprocess(request):
    """
        Kill the target process (along with all of its child processes) and return
        the killed pid
        
        Note that the process is NOT deleted from the dict of runnning processes.
    """
    
    #get target pid
    targetPID = int(request.POST.get('pid'))

    
    #kill all child processes first
    print('\n***********killing ', targetPID, '**************************')
    current_process = psutil.Process(targetPID)
    children = current_process.children(recursive=True)
    if len(children) >= 1:
        for child in children:
            print('Killing child pid: {}\n'.format(child.pid))
            child.kill()
    else:
        print('\n----Process has no children----\n')
    

    #kill target process
    for pid in procs.keys():
        if pid == targetPID:
            procs[pid].kill()
    
           
    
    #return killed pid
    data = {'pid': targetPID}
    return JsonResponse(data)
    