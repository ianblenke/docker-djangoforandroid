from django.shortcuts import render
from django.http import JsonResponse
from subprocess import Popen, PIPE
#from django.views.decorators.csrf import csrf_exempt
import psutil
from threading import Thread
import signal
#import time



#dict of running processes
#{KEYS: pids,  VALUES: process objects}
procs = {}   

#dict of scripts (in services folder)
#{KEYS: simplified script name, VALUES: actual script (string)}
scripts = {"tor": "exec screen -D -m -S tor tor", "gotty": "exec gotty -w --port ${PORT:-8090} screen -r -d tor" } 

#Separate process used to scan running processes and check their statuses
processScanner = None



"""NOTES:
        - Downloaded Go v1.10
        - Downloaded gotty
        - 'exec' required to keep shell (opened by Popen()) open
        - When starting process with 'screen', use -D to keep it attached and able to be
            discovered by python
        - You have to first create an env and then set the path to use gotty 
            (-->  $GOBIN/gotty && export PATH="$PATH:$GOBIN" && source ~/.profile)
        
        - sudo netstat -plnt (check status of all ports)
        - sudo killall tor
        
TODO's:

        1. Create separate thread/process to monitor status of all processes
            and have a way to restart somethingthat has stopped
        2. Standardize everything so that we only have to add a txt file
            with the shell command(s)/scripts into a "services" folder
            andeverything else is taken care of
                i.e. adding myScript.txt to the 'services' folder will 
                automatically create a new button in the control hub
                that runs the script specified in myScripts.txt
        3. CLEANUP CODE!! (especially javascript)
        
"""


def checkProcessStatuses(request):
    """
        Uses a thread to continuously check the status of all processes in procs.
        It deletes them from the table and procs list if they are not found in ps (running processes).
        
        Notes: 
            
    """
    
    """*****The problem is currently here (see javascript for more details).*****"""
    
    closed = []
    for process in list(procs.keys()):       #search all processes in the current list
        p = psutil.Process(process)

        print(p.pid, ':', p.as_dict(attrs=['status']))
        if process not in psutil.pids() or p.status() == psutil.STATUS_ZOMBIE:         #if the process is no longer running 
            closed.append(process)
            print('Bad close of pid', process)
        
    #return list of closed pids
    return JsonResponse({'closed': closed})




def androidprocessmanager(request):
    
    global processScanner    

    #start the process scanner thread if it hasn't been already
#    if processScanner is None:
#        processScanner = Thread(name = 'Process Scanner', target=checkProcessStatuses)
#        processScanner.start()
    
    
    """return home page"""
    return render(request, "androidprocessmanager.html", {})




def startprocess(request):  
    """
        Start the target process, save its name/pid to a list, and return them as
        data
    """
    
    if __name__ == '__main__':
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        
    processName = request.POST.get("processName")       #get name of process/button pressed
    shellcmd = scripts[processName]                     #get corresponding script
    proc= Popen(shellcmd, stdout=PIPE, shell = True)    #start process
    procs[proc.pid] = proc                              #add to list of running processes
    
    
    data = {'pid': proc.pid, 'name': processName}       #package and send data
    return JsonResponse(data)
    
    




#@csrf_exempt
def stopprocess(request, badclose = None):
    """
        Kill the target process (along with all of its child processes) and return
        the killed pid
    """
    
    if __name__ == '__main__':
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    
    #if correctly closed (closed using services manager)
    if badclose is None:
        #get target pid
        targetPID = int(request.POST.get('pid'))
        
        
        #kill all child processes first
        print('\n**********killing ', targetPID, '**************')
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
    #incorrectly closed (closed outside services manager)
    else:                                
        targetPID = badclose
    
    
    #delete entry from procs
    del procs[targetPID]
    
    #return killed pid
    data = {'pid': targetPID}
    return JsonResponse(data)
    