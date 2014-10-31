var pdays = new Array();
var pmonths = new Array();
var pyears = new Array();
var pshares = new Array();
var pvalues = new Array();
var sdays = new Array();
var smonths = new Array();
var syears = new Array();
var sshares = new Array();
var svalues = new Array();
var jsonData;
var row, cell, table;
var flag = 0;

// # of input rows
var inputCount = 10;

function firstLoad(){
	table = document.getElementById("purchases");
	for(i = 0; i < inputCount; i++){
		row = table.insertRow(i+1);
		cell = row.insertCell(0);
		cell.innerHTML = '<input type="text" id="pday'+ i +'" class="form-control">';
		cell.className = 'col-md-1';
		
		cell = row.insertCell(1);
		cell.innerHTML = '<input type="text" id="pmonth'+ i +'" class="form-control">';
		cell.className = 'col-md-1';
		
		cell = row.insertCell(2);
		cell.innerHTML = '<input type="text" id="pyear'+ i +'" class="form-control">';
		cell.className = 'col-md-1';
		
		cell = row.insertCell(3);
		cell.innerHTML = '<input type="text" id="pshare'+ i +'" class="form-control">';
		cell.className = 'col-md-2';
		
		cell = row.insertCell(4);
		cell.innerHTML = '<div class="input-group"><span class="input-group-addon">$</span><input type="text" id="pvalue'+ i +'" class="value form-control">';
		cell.className = 'col-md-6';
	}
	
	table = document.getElementById("sales");
	for(i = 0; i < inputCount; i++){
		row = table.insertRow(i+1);
		cell = row.insertCell(0);
		cell.innerHTML = '<input type="text" id="sday'+ i +'" class="form-control">';
		cell.className = 'col-md-1';
		
		cell = row.insertCell(1);
		cell.innerHTML = '<input type="text" id="smonth'+ i +'" class="form-control">';
		cell.className = 'col-md-1';
		
		cell = row.insertCell(2);
		cell.innerHTML = '<input type="text" id="syear'+ i +'" class="form-control">';
		cell.className = 'col-md-1';
		
		cell = row.insertCell(3);
		cell.innerHTML = '<input type="text" id="sshare'+ i +'" class="form-control">';
		cell.className = 'col-md-2';
		
		cell = row.insertCell(4);
		cell.innerHTML = '<div class="input-group"><span class="input-group-addon">$</span><input type="text" id="svalue'+ i +'" class="value form-control">';
		cell.className = 'col-md-6';
	}
}

function inputToJSON(){
	// Store input values into variables
	for(i = 0; i < 10; i++){
		pdays[i] = $("#pday" + i).val();
		pmonths[i] = $("#pmonth" + i).val();
		pyears[i] = $("#pyear" + i).val();
		pshares[i] = $("#pshare" + i).val();
		pvalues[i] = $("#pvalue" + i).val();
		
		sdays[i] = $("#sday" + i).val();
		smonths[i] = $("#smonth" + i).val();
		syears[i] = $("#syear" + i).val();
		sshares[i] = $("#sshare" + i).val();
		svalues[i] = $("#svalue" + i).val();
	}
	
	// Format data into JSON
	jsonData = '{"buy":[';
	for(i = 0; i < inputCount; i++){
		// Rough validation (days is empty)
		if(pdays[i] != ''){
			jsonData += '{"number":' + pshares[i] + ',"price":' + pvalues[i] + ',"year":' + pyears[i] + ',"month":' + pmonths[i] + ',"day":' + pdays[i] + '}';
			jsonData += ','
		}
	}
	jsonData = jsonData.substring(0, jsonData.length - 1);
	jsonData += '],"sell":[';
	for(i = 0; i < inputCount; i++){
		if(sdays[i] != ''){
			jsonData += '{"number":' + sshares[i] + ',"price":' + svalues[i] + ',"year":' + syears[i] + ',"month":' + smonths[i] + ',"day":' + sdays[i] + '}';
			jsonData += ','
		}
	}
	jsonData = jsonData.substring(0, jsonData.length - 1);
	jsonData += ']}';
	
/*
	$.ajax( "/compute",
	    ({type: "POST",
		data: jsonData,
		contentType: "application/json",
		success: handle_response,
		error: function(data) {
			document.open();
			document.write(data.responseText);
			document.close();
		}
	    }))
*/
}

function handle_response(data){
	$( "#request-data" ).val( JSON.stringify(data, null, 3) );
}