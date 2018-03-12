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





/*deletes row from running-processes table, corresponding to the "Stop" button that was pressed*/
function deleteRow(r) {
	
   var rowNumber = r.parentNode.parentNode.rowIndex;
   
   document.getElementById("processesTable").deleteRow(rowNumber);
	
	numProcesses = numProcesses - 1;
	updateRows();
}




/*Match table row with its corresponding process (called after addRow and deleteRow)*/
function updateRows(){
	procRows = {};                                                                          //delete current processes list
	var row;
	
	for(var i = 0; i < numProcesses; ++i){
		
		var name = document.getElementById("processesTable").rows[i+1].cells[0].innerHTML;  //read process names directly from table
		var pid = document.getElementById("processesTable").rows[i+1].cells[1].innerHTML;   //read pids directly from table
		row = i+1;
		procRows[name.replace(/\s/g, '')] = [name, pid, row];                               //re-write processes list 
	}
	
}




function runProcess1(){

	var date = new Date();
	var time = date.getTime();
	
	//disable process 1 button
	document.getElementById("opentor").disabled = true;
	
	//start process 1 
	$.ajax({
			type: "GET",
			dataType: "json",
			url: "webpage2/",
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
			type: "GET",
			dataType: "json",
			url: "webpage3/",
			success: function(result){
				console.log(result);
				addRow(result.name, result.pid);
			}, 
			error: function(jqxhr, stat, exception){
				alert("calculator failed to start properly");
			}
	});  
}




/* Implements all process-closing procedures*/
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
		url: "webpage4/", 
		success: function(result){
			console.log(result);
			deleteRow(process);       //delete corresponding row from table
		},
		error: function(jqxhr, stat, exception){
			alert('Process failed to shutdown\n' + exception.responseText);
		}
	});
}


