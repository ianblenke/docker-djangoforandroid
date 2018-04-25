"""NOTES:
        - Downloaded Go v1.10
        - Downloaded gotty
        - ***You have to first create an env and then set the path in order to use gotty 
            (-->  $GOBIN/gotty && export PATH="$PATH:$GOBIN" && source ~/.profile)
        - 'exec' command is required in each 'scripts' dict entry 
            It serves to close the shell and hand its pid to the child
        - When starting process with 'screen', use -D to keep it attached and able to be
            discovered by python
        - Useful debugging commands
            - sudo netstat -plnt (check status of all ports)
            - sudo killall tor
            - sudo kill -9 pid
        
TODO's:

        1. Create a way to restart something that has stopped
        2. Standardize everything so that we only have to add a txt file
            with the shell command(s)/scripts into a "services" folder
            andeverything else is taken care of
                i.e. adding myScript.txt to the 'services' folder will 
                automatically create a new button in the control hub
                that runs the script specified in myScripts.txt
        
"""


from django.shortcuts import render
from django.http import JsonResponse
from subprocess import Popen, PIPE
import psutil
import signal



#dict of running processes
#{KEYS: pids,  VALUES: process objects}
procs = {}   

#dict of scripts (in services folder)
#{KEYS: simplified script name, VALUES: actual script (string)}
scripts = {"tor": "exec screen -D -m -S tor tor", 
           "gotty": "exec gotty -w --port ${PORT:-8090} screen -r -d tor" } 





def androidprocessmanager(request):    
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
        
        ********************************************************************************************
        The problem is when you try to close a process started from outside the UI; aka "bad starts"
        ********************************************************************************************
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





def checkProcessStatuses(request):
    """
        Crosschecks all processes in 'procs' list with those in psutil.pids().
        It deletes them from the UI table and from 'procs' list if they are zombies or
        they are not found in ps (running processes).            
    """
    
    closed = []
    
    #check for bad closes
    for process in list(procs.keys()):                                                 #search all processes in the current list
        p = psutil.Process(process)

        print(p.pid, ':', p.as_dict(attrs=['status']))
        if process not in psutil.pids() or p.status() == psutil.STATUS_ZOMBIE:         #process is zombie or no longer running 
            closed.append(process)
            print('Bad close of pid', process)
    
    
    #erase closed pids from 'procs' list
    for process in closed:
        del procs[process]
    
    
    
    #return list of closed pids
    return JsonResponse({'closed': closed})    