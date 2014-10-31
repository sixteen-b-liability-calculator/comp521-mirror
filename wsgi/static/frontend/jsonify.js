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

// # of input rows
var inputCount = 10;

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