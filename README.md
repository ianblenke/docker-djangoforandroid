# docker-djangoforandroid

## Building

This is based on djangoforandroid and the example project from that. 

User interface location: 
    docker-djangoforandroid->templates->androiprocessmanager.html
    docker-djangoforandroid->static->Homepage->homepagescripts.js
    
Django (server side) location:
    docker-djangoforandroid->androidprocessmanager->urls.py
    docker-djangoforandroid->androidprocessmanager->views.py
    docker-djangoforandroid->androidprocessmanager->settings.py
    
To test:
    1. Open shell and navigate to docker-djangoforandroid
    2. (This is in order to use gotty) Enter the following commands separately
        $GOBIN/gotty
        export PATH="$PATH:$GOBIN" 
        source ~/.profile
    3. Enter "python3 manage.py runserver"  (excluding quotations)
        (The django server is now running)
    4. Open a web browser and go to the following address:
        http://127.0.0.1:8000/androidprocessmanager/
        (You should see the user interface (html file above))
    - You should now be able to start processes by pressing the corresponding 
      button. Tor runs in the background, but you can use the netstat command to 
      check that it's running and on which port it is running. Gotty also runs on
      its own port and should be seen with the same netstat command. Additionally,
      you can navigate to the following address on a separate browser tab after
      Gotty has started:
        http://127.0.0.1:8090/
      There, you should see a shell-like interface if the process is running correctly.
    - While testing, you may find the following command useful:
        sudo killall tor
      This is because tor sometimes defaults to automatically restart after it has been 
      closed (not what we want).



To build:

    make

The resultant output `.apk` file will be in the `outputs/` folder.

