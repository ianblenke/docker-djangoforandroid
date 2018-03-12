from django.shortcuts import render
from django.http import JsonResponse
from subprocess import Popen, PIPE
import psutil



procs = {}   #list of running processes
             #{KEYS: pids,  VALUES: process objects}




"""NOTES:
        - Downloaded Go v1.10
        - Downloaded gotty
        - 'exec' required to keep shell (opened by Popen()) open
        - When starting process with 'screen', use -D to keep it attached and able to be
            discovered by python
        
        - sudo netstat -plnt (check status of all ports)
        
TODO's:
        1. Converge and rename 'webpage#' functions below.
            - Will require a POST from javascript file to specify which 
            process to open
        2. Create separate thread/process to monitor status of all processes
            and have a way to restart somethingthat has stopped
        3. Standardize everything so that we only have to add a txt file
            with the shell command(s)/scripts into a "services" folder
            andeverything else is taken care of
                i.e. adding myScript.txt to the 'services' folder will 
                automatically create a new button in the control hub
                that runs the script specified in myScripts.txt
        
"""






def webpage1(request):
    
    return render(request, "webpage1.html", {})




def webpage2(request):  
    """This method requires a string representation of shell command(s) to be executed
    """
       
    shellcmd = "exec screen -D -m -S tor tor"           #define shell command   
                                                        
                   
    proc= Popen(shellcmd, stdout=PIPE, shell = True)    #start process
    procs[proc.pid] = proc                              #add to list of running processes
    
    
    data = {'pid': proc.pid, 'name': 'tor'}             #package and send data

    return JsonResponse(data)
    
    




def webpage3(request):
    """This method requires a string representation of shell command(s) to be executed
    """
       
    #define shell command
    shellcmd= "exec gotty -w --port ${PORT:-8090} screen -r -d tor"   
                
    proc= Popen(shellcmd, stdout=PIPE, shell = True)    #start process
    procs[proc.pid] = proc                              #add to list of running processes
    
    
    data = {'pid': proc.pid, 'name': 'gotty'}           #package and send data
    
    return JsonResponse(data)




def webpage4(request):
    """Kill target process (along with all of its child processes)"""
    #get target pid
    targetPID = int(request.POST.get('pid'))

    
    #kill all child processes first
    print('***********killing ', targetPID, '**************************')
    current_process = psutil.Process(targetPID)
    children = current_process.children(recursive=True)
    if len(children) >= 1:
        for child in children:
            print('Killing child pid: {}'.format(child.pid))
            child.kill()
    else:
        print('----Process has no children----')
    

    #kill target process
    for pid in procs.keys():
        if pid == targetPID:
            procs[pid].kill()
    
           
    
    #return killed pid
    data = {'pid': targetPID}
    return JsonResponse(data)
    