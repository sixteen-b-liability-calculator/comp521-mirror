var defaultInputCount = 10;

function removePSRow(button){
    button.parentElement.parentElement.remove();
}

function insertPSRow(table){
    i = table.rows.length
    row = table.insertRow();

    cell = row.insertCell();
    cell.innerHTML = '<input type="button" id="remove" value="X" class="form-control" onClick="removePSRow(this);">';

    cell = row.insertCell();
    cell.innerHTML = '<input type="text" id="month" class="form-control">';
    cell.className = 'col-md-1';
    
    cell = row.insertCell();
    cell.innerHTML = '<input type="text" id="day" class="form-control">';
    cell.className = 'col-md-1';
    
    cell = row.insertCell();
    cell.innerHTML = '<input type="text" id="year" class="form-control">';
    cell.className = 'col-md-1';
    
    cell = row.insertCell();
    cell.innerHTML = '<input type="text" id="shares" class="form-control">';
    cell.className = 'col-md-2';
    
    cell = row.insertCell();
    cell.innerHTML = '<div class="input-group"><span class="input-group-addon">$</span><input type="text" id="value" class="value form-control">';
    cell.className = 'col-md-6';

    return row;
}

function firstLoad(){
    purchases = $("#purchases")[0];
    sales = $("#sales")[0];
    for(i = 0; i < defaultInputCount; ++i){
	insertPSRow(purchases);
	insertPSRow(sales);
    }
}

function purchaseRow(){
    purchases = $("#purchases")[0];
    insertPSRow(purchases);
}

function saleRow(){
    sales = $("#sales")[0];
    insertPSRow(sales);
}

function eltFromRow(row){
    elt = {};
    elt.price = parseInt($("#value", row).val());
    elt.day = parseInt($("#day", row).val());
    elt.month = parseInt($("#month", row).val());
    elt.year = parseInt($("#year", row).val());
    elt.number = parseInt($("#shares", row).val());
    return elt;
}


function inputToJSON(){
    purchasesTable = $("#purchases")[0];
    salesTable = $("#sales")[0];
    purchases = []
    sales = []
    for(i = 1; i < purchasesTable.rows.length; ++i){
	row = purchasesTable.rows[i];
	elt = eltFromRow(row);
	if(! isNaN(elt.price)){
	    purchases.push(elt);
	}
    }
    for(i = 1; i < salesTable.rows.length; ++i){
	row = salesTable.rows[i];
	elt = eltFromRow(row);
	if(! isNaN(elt.price)){
	    sales.push(elt);
	}
    }
    $.ajax( "/compute",
	({type: "POST",
	    data: $.toJSON({ "buy": purchases, "sell": sales }),
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
	
	testData = JSON.stringify(data).split("\"");
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

function pullSEC(){
	secStartYear = $("#secStartYear").val();
	secStartMonth = $("#secStartMonth").val();
	secEndYear = $("#secEndYear").val();
	secEndMonth = $("#secEndMonth").val();

	secCIK = $("#secCIK").val();
	
	secJSON = '{ "startYear":'+secStartYear+',"startMonth":'+secStartMonth+',"endYear":'+secEndYear+',"endMonth":'+secEndMonth+',"cik":'+secCIK+'}';

	$.ajax( "/pullSEC",
	    ({type: "POST",
		data: secJSON,
		contentType: "application/json",
		success: populate,
		error: function(data) {
			document.open();
			document.write(data.responseText);
			document.close();
		}
	}))
}

function populate(data){
	$('#myTabs li:eq(0) a').tab('show');

	$("#purchases tr:gt(0)").remove();
	$("#sales tr:gt(0)").remove();
	
	var secData = JSON.stringify(data).split("\"");
	
	var month,day,year,number,price;
	
	for(j = 0; j < secData.length; j++){
		var exitFlag = true;
    	if(secData[j] == "buys"){
    		// Populate Purchases
			table = document.getElementById("purchases");
			var rowCount = 0;
    	
    		i = j+2;
    		do{
		    	day = secData[i+1].substring(0, secData[i+1].length-1).substring(1);
		    	month = secData[i+3].substring(0, secData[i+3].length-1).substring(1);
		    	number = secData[i+5].substring(0, secData[i+5].length-1).substring(1);
		    	price = secData[i+7].substring(0, secData[i+7].length-1).substring(1);
		    	year = secData[i+9].substring(0, secData[i+9].length-3).substring(1);
		    	
		    	row = table.insertRow(rowCount+1);
			
				cell = row.insertCell(0);
				cell.innerHTML = '<input type="text" id="pmonth'+ i +'" class="form-control" value="'+ month +'">';
				cell.className = 'col-md-1';
				
				cell = row.insertCell(1);
				cell.innerHTML = '<input type="text" id="pday'+ i +'" class="form-control" value="'+ day +'">';
				cell.className = 'col-md-1';
				
				cell = row.insertCell(2);
				cell.innerHTML = '<input type="text" id="pyear'+ i +'" class="form-control" value="'+ year +'">';
				cell.className = 'col-md-1';
				
				cell = row.insertCell(3);
				cell.innerHTML = '<input type="text" id="pshare'+ i +'" class="form-control" value="'+ number +'">';
				cell.className = 'col-md-2';
				
				cell = row.insertCell(4);
				cell.innerHTML = '<div class="input-group"><span class="input-group-addon">$</span><input type="text" id="pvalue'+ i +'" class="value form-control" value="'+ price +'">';
				cell.className = 'col-md-6';
				
				rowCount++;
				
				if(secData[i+10] == "sells"){
					exitFlag = false;
				}else{
					i+=10;
				}
			}while(exitFlag);
    	}
    	
    	var exitFlag = true;
    	if(secData[j] == "sells"){
    		// Populate Purchases
			table = document.getElementById("sales");
			var rowCount = 0;
			
    		i = j+2;
    		do{
		    	day = secData[i+1].substring(0, secData[i+1].length-1).substring(1);
		    	month = secData[i+3].substring(0, secData[i+3].length-1).substring(1);
		    	number = secData[i+5].substring(0, secData[i+5].length-1).substring(1);
		    	price = secData[i+7].substring(0, secData[i+7].length-1).substring(1);
		    	year = secData[i+9].substring(0, secData[i+9].length-3).substring(1);
		    	
		    	row = table.insertRow(rowCount+1);
			
				cell = row.insertCell(0);
				cell.innerHTML = '<input type="text" id="smonth'+ i +'" class="form-control" value="'+ month +'">';
				cell.className = 'col-md-1';
				
				cell = row.insertCell(1);
				cell.innerHTML = '<input type="text" id="sday'+ i +'" class="form-control" value="'+ day +'">';
				cell.className = 'col-md-1';
				
				cell = row.insertCell(2);
				cell.innerHTML = '<input type="text" id="syear'+ i +'" class="form-control" value="'+ year +'">';
				cell.className = 'col-md-1';
				
				cell = row.insertCell(3);
				cell.innerHTML = '<input type="text" id="sshare'+ i +'" class="form-control" value="'+ number +'">';
				cell.className = 'col-md-2';
				
				cell = row.insertCell(4);
				cell.innerHTML = '<div class="input-group"><span class="input-group-addon">$</span><input type="text" id="svalue'+ i +'" class="value form-control" value="'+ price +'">';
				cell.className = 'col-md-6';
				
				rowCount++;
				
				if(secData[i+10] == ""){
					exitFlag = false;
				}else{
					i+=10;
				}
			}while(exitFlag);
    	}
    }
}
