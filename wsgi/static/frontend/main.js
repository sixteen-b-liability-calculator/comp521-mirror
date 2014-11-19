// Lazy code, will consolidate soon.
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
var testData;

var returnData = '{"pairs":[{"buy": {"day": 29,"month": 10,"number": 28,"price": 1879,"year": 5},"count": 10,"sell": {"day": 14,"month": 12,"number": 10,"price": 9872,"year": 5}},{"buy": {"day": 3,"month": 5,"number": 29,"price": 109,"year": 5},"count": 23,"sell": {"day": 8,"month": 8,"number": 23,"price": 1987,"year": 5}},{"buy": {"day": 3,"month": 5,"number": 29,"price": 109,"year": 5},"count": 6,"sell": {"day": 29,"month": 6,"number": 29,"price": 1827,"year": 5}}],"status": "optimal","value": 133432}';

// # of input rows
var inputCount = 10;

// page's first page load. two tabs
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
	// Store input values into arrays
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
			jsonData += '{"number":' + pshares[i] + ',"price":' + pvalues[i] + ',"year":' + pyears[i] + ',"month":' + pmonths[i] + ',"day":' + 				pdays[i] + '}';
			jsonData += ','
		}
	}
	jsonData = jsonData.substring(0, jsonData.length - 1);
	jsonData += '],"sell":[';
	for(i = 0; i < inputCount; i++){
		if(sdays[i] != ''){
			jsonData += '{"number":' + sshares[i] + ',"price":' + svalues[i] + ',"year":' + syears[i] + ',"month":' + smonths[i] + ',"day":' + 				sdays[i] + '}';
			jsonData += ','
		}
	}
	jsonData = jsonData.substring(0, jsonData.length - 1);
	jsonData += ']}';
	// End format data

	
	$.ajax( "/compute",
	    ({type: "POST",
		data: jsonData,
		contentType: "application/json",
		success: printOutput,
		error: function(data) {
			document.open();
			document.write(data.responseText);
			document.close();
		}
	}))
	
	// Switches to second tab
	$('#myTabs li:eq(1) a').tab('show');
}

function printOutput(data){
	
	testData = JSON.stringify(data);
	alert(testData);
    testData = newData.split("\"");
    var pday, pmonth, pnumber, pprice, pyear, sday, smonth, snumber, sprice, syear, count;
    table = document.getElementById("pairings");
    var pairingsRow = 0;
    var maxprofit = 0;
    
    //{"pairs":[{"buy": {"day": 29,"month": 10,"number": 28,"price": 1879,"year": 5},"count": 10,"sell": {"day": 14,"month": 12,"number": 10,"price": 9872,"year": 5}},{"buy": {"day": 3,"month": 5,"number": 29,"price": 109,"year": 5},"count": 23,"sell": {"day": 8,"month": 8,"number": 23,"price": 1987,"year": 5}},{"buy": {"day": 3,"month": 5,"number": 29,"price": 109,"year": 5},"count": 6,"sell": {"day": 29,"month": 6,"number": 29,"price": 1827,"year": 5}}],"status": "optimal","value": 133432}
    
    //{"pairs":[{"buy":{"day":3,"month":4,"number":6,"price":10,"year":5},"count":6,"sell":{"day":5,"month":5,"number":200,"price":1029,"year":5}},{"buy":{"day":3,"month":4,"number":30,"price":500,"year":5},"count":30,"sell":{"day":5,"month":5,"number":200,"price":1029,"year":5}},{"buy":{"day":3,"month":4,"number":8,"price":20,"year":5},"count":8,"sell":{"day":5,"month":5,"number":200,"price":1029,"year":5}}],"status":"optimal","value":30056}
    
    for(i = 0; i < testData.length; i++){
    	if(testData[i] == "buy"){
	    	pday = testData[i+3].substring(0, testData[i+3].length-1).substring(1);
	    	pmonth = testData[i+5].substring(0, testData[i+5].length-1).substring(1);
	    	pnumber = testData[i+7].substring(0, testData[i+7].length-1).substring(1);
	    	pprice = testData[i+9].substring(0, testData[i+9].length-1).substring(1);
	    	pyear = testData[i+11].substring(0, testData[i+11].length-2).substring(1);
	    	
	    	count = testData[i+13].substring(0, testData[i+13].length-1).substring(1);
	    	
	    	sday = testData[i+17].substring(0, testData[i+17].length-1).substring(1);
	    	smonth = testData[i+19].substring(0, testData[i+19].length-1).substring(1);
	    	snumber = testData[i+21].substring(0, testData[i+21].length-1).substring(1);
	    	sprice = testData[i+23].substring(0, testData[i+23].length-1).substring(1);
	    	syear = testData[i+25].substring(0, testData[i+25].length-4).substring(1);
	    	
	    	pairingsRow++;
			row = table.insertRow(pairingsRow);
			cell = row.insertCell(0);
			cell.innerHTML = pmonth + '/' + pday + '/' + pyear;
			cell.className = 'col-md-1';
			cell = row.insertCell(1);
			cell.innerHTML = '$' + pprice;
			cell.className = 'col-md-1';
			cell = row.insertCell(2);
			cell.innerHTML = smonth + '/' + sday + '/' + syear;
			cell.className = 'col-md-1';
			cell = row.insertCell(3);
			cell.innerHTML = '$' + sprice;
			cell.className = 'col-md-1';
			cell = row.insertCell(4);
			cell.innerHTML = count;
			cell.className = 'col-md-1';
			cell = row.insertCell(5);
			var profit = count*sprice - count*pprice;
			cell.innerHTML = '$' + profit;
			cell.className = 'col-md-1';
			maxprofit += profit;
    	}
    }
    // Add summation line
    row = table.insertRow(pairingsRow+1);
    for(i = 0; i < 5; i++){
    	row.insertCell(i);
    }
    cell = row.insertCell(5);
    cell.innerHTML = '___________';
    
    // Add max profit
    row = table.insertRow(pairingsRow+2);
    for(i = 0; i < 4; i++){
    	row.insertCell(i);
    }
    cell = row.insertCell(4);
    cell.innerHTML = '<strong>Total</strong>';
    cell = row.insertCell(5);
    cell.innerHTML = '$' + maxprofit;
    
    // <form action="save.php" method="post" id="save"><input type="submit" class="btn btn-default col-md-6" value="Save Data"></form>
}