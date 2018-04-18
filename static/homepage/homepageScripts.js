/*
*
* NOTES:
* 
* Start buttons (top of webpage1.html) are named id="open" + processname
* Stop buttons (each row) are named id=processname
*
*
* When adding new processes:
*		1) add button to btn-group in webpage1.html
*				- id="open" + processname, text="Process Name"
*		2) create runProcess function like those below
*		3) create view in views.py like those shown in the file
*/



var numProcesses = 0;
var procRows = {}; //keeps up with row-process pairs { KEYS: processname, VALUES: [name, pid, row]}



/****************************************************************************************************
Notes:

	1) USE CONSOLE.LOG TO DEBUG!!!!!!!!!!!!!
	2) Everything works perfectly when ran from inside the task manager
	3) You're current issue is inside DJANGO....
		- Django keeps sending the zombie process to javascript, which doesn't exist in procRows so you get undefined values
		- The reason Django keeps sending it is because of the "if closed or zombie" statement
		- To solve this, either change the if statement or better yet, go to "https://mail.python.org/pipermail/tutor/2003-December/026748.html"
			and read the last three things on that page to ignore (SIG_IGN) the zombie processes.
		- You can also read up on flag controls in subprocess module
	4) Right now the program works as expected for the first "bad_close." The problem starts after that bc it is now a zombie process
		and will keep sending that pid from Django. WATCH THE CONSOLE while troubleshooting
	
*****************************************************************************************************/





function checkstatuses(){
	
   setInterval(function(){
   
      $.ajax({ type:"GET", url: "checkprocesses/", dataType: "json", success: function(data){
			
			if (data.closed.length > 0){
				console.log('********Django sent back a badly closed process************');
				for(var i = 0; i < data.closed.length; ++i){
					//delete badly closed pid from table
					
					deleteRow(0, data.closed[i]);

					//re-enable button
					
				}
				
			}
        
      }});
  }, 15000);
};

checkstatuses();




/*adds new row to running-processes table*/
function addRow(pname, pid){
	
	// get table
	var table = document.getElementById("processesTable");
	
	
	// add 1 row to the table:
	var row = table.insertRow(-1);


	// add 3 columns to the row
	var cell1 = row.insertCell(0);
	var cell2 = row.insertCell(1);
	var cell3 = row.insertCell(2);
	

	// Fill in the new cells:
	cell1.innerHTML = pname;
	cell2.innerHTML = pid;
	cell3.innerHTML = "<td><input type='button' id=" + pname.replace(/\s/g, '') + " value='Stop' onclick='closeProcess(this)'></td>"
	
	
	// increment number of processes
	numProcesses = numProcesses + 1; 
	
	
	updateRows();
}




/*searches procRows for the process 'name' corresponding to 'pid'*/
function pidToName(pid) {
	
		
		for (var item in procRows){

			if (procRows[item][1] == String(pid)) {    
				return procRows[item][0];                //return the name of that item
			}		
		}
		
		
		return null;                                   //return null if pid not found
}





/*deletes row from running-processes table, corresponding to the "Stop" button that was pressed*/
function deleteRow(r, bad_pid = null) {
	
	
	var rowNumber;	    //table row corresponding to the target process
	
	//set rowNumber
	if(bad_pid === null){
		
		//gotten from the "delete" button that was pressed
   	rowNumber = r.parentNode.parentNode.rowIndex;
   	
   }
   else{
   	
   	//gotten directly from parameter 
   	//this was the result of a 'bad close' called from checkstatuses())
   	var bad_proc = pidToName(bad_pid);                   
   	//re-enable start button
		//document.getElementById('open' + bad_proc).disabled = false;                
   	console.log('bad_proc (nameof bad process): ' + bad_proc);
		rowNumber = procRows[bad_proc][2];                                   
		console.log('target table rowNumber set to: ' + rowNumber);
		
   }                                                                       
   console.log('passed setting rowNumber()');
   
   
   //delete the row element and update the table
   document.getElementById("processesTable").deleteRow(rowNumber);         
   console.log('passed deleteRow()');	
	
	//decrement number of processes
	numProcesses = numProcesses - 1;
	
	updateRows();                                                           
	console.log('passed updateRows()');
	
	
	var procRowsLen = Object.keys(procRows).length;                         
	console.log('numProcess: ' + String(numProcesses) + '  ' + 'procrowslen: ' + procRowsLen);
}





/*Match table row with its corresponding process (called after addRow and deleteRow)*/
function updateRows(){
	procRows = {};                                                                          //delete current processes list
	var row;
	console.log('inside updateRows()');
	var tableSize = document.getElementById("processesTable").rows.length;
	tableSize -= 1; //bc the header row doesn't count
	console.log('tablesize: ' + String(tableSize));
	for(var i = 0; i < tableSize; ++i){
		
		var name = document.getElementById("processesTable").rows[i+1].cells[0].innerHTML;  //read process names directly from table
		var pid = document.getElementById("processesTable").rows[i+1].cells[1].innerHTML;   //read pids directly from table
		row = i+1;
		procRows[name.replace(/\s/g, '')] = [name, pid, row];                               //re-write processes list
		console.log('procRows[' + row + ']' + 'after ' + procRows[name.replace(/\s/g, '')]); 
	}
	console.log('leaving updateRows');
}





function runProcess1(){

	var date = new Date();
	var time = date.getTime();
	
	//disable process 1 button
	document.getElementById("opentor").disabled = true;
	
	//start process 1 
	$.ajax({
			type: "POST",
			dataType: "json",
			data: {'processName': "tor"},
			url: "startprocess/",
			success: function(result){
				console.log(result);
				addRow(result.name, result.pid);
			}, 
			error: function(jqxhr, stat, exception){
				alert("tor failed to start properly");
			}
	});  
}



function runProcess2(){
	
	var date = new Date();
	var time = date.getTime();
	
	//disable process 2 button
	document.getElementById("opengotty").disabled = true;
	
	//start process 2
	$.ajax({
			type: "POST",
			dataType: "json",
			data: {'processName': "gotty"},
			url: "startprocess/",
			success: function(result){
				console.log(result);
				addRow(result.name, result.pid);
			}, 
			error: function(jqxhr, stat, exception){
				alert("calculator failed to start properly");
			}
	});  
}





/* Implements all process-closing procedures for 'process'*/
function closeProcess(process){
	
	//re-enable start button
	document.getElementById('open' + process.id).disabled = false;
	
	
	
	//get target PID (from procRows) using process name
	var pid = procRows[process.id][1];
	
	
	//send target PID to django
	$.ajax({
		type: "POST",
		datatype: "json",
		data: {'pid': pid},
		url: "stopprocess/", 
		success: function(result){
			console.log(result);
			deleteRow(process);       //delete corresponding row from table
		},
		error: function(jqxhr, stat, exception){
			alert('Process failed to shutdown\n' + exception.responseText);
		}
	});
}



