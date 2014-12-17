var defaultInputCount = 10;

// Removes row of data
function removePSRow(button){
    button.parentElement.parentElement.remove();
}

// Inserts empty row for acquisitions or disposal table
function insertPSRow(table){
    row = table.insertRow();

    cell = row.insertCell();
    cell.innerHTML = '<input type="button" id="remove" value="Remove Row" class="btn btn-default btn-xs" onClick="removePSRow(this);">';

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
    cell.className = 'col-md-3';
    
    cell = row.insertCell();
    cell.innerHTML = '<div id="title"></div>';
    cell.className = 'col-md-1';
    
    cell = row.insertCell();
    cell.innerHTML = '<div id="ownership"></div>';
    cell.className = 'col-md-1';
    
    cell = row.insertCell();
    cell.innerHTML = '<div id="filing"></div>'
    cell.className = 'col-md-1';

    return row;
}

// Called by <body> onload
function firstLoad(){
    purchases = $("#purchases")[0];
    sales = $("#sales")[0];
    for(i = 0; i < defaultInputCount; ++i){
    	insertPSRow(purchases);
    	insertPSRow(sales);
    }
}

// Called by "Add Row" button for Acquisitions table
function purchaseRow(){
    purchases = $("#purchases")[0];
    insertPSRow(purchases);
}

// Called by "Add Row" button for Disposals table
function saleRow(){
    sales = $("#sales")[0];
    insertPSRow(sales);
}

// Called in inputToJSON() to store living input data
function readTable(table){
    out = []
    for(i = 1; i < table.rows.length; ++i){
    	row = table.rows[i];
    	elt = new Object();
    	elt.price = parseFloat($("#value", row).val());
    	elt.day = parseFloat($("#day", row).val());
    	elt.month = parseFloat($("#month", row).val());
    	elt.year = parseFloat($("#year", row).val());
    	elt.number = parseFloat($("#shares", row).val());
    	if(!isNaN(elt.price)){
    	    out.push(elt);
    	}
    }
    return out;
}

// Calculates with linear programming
function inputToJSON(url){
    purchases = readTable($("#purchases")[0]);
    sales = readTable($("#sales")[0]);
    
    email = $("#email").val()
    
    stella = document.getElementById("stella").selected;
    jammies = document.getElementById("jammies").selected;
    if(jammies){
	    stella = true;
    }

    $.ajax( url,
	({type: "POST",
	    data: $.toJSON({ "buy": purchases, "sell": sales, "stella_correction": stella, "jammies_correction": jammies, "recipient": email }),
	    contentType: "application/json",
        dataType: "json",
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

// Calculate with greedy algorithm
function greedy(){
    purchases = readTable($("#purchases")[0]);
    sales = readTable($("#sales")[0]);
    
    email = $("#email").val()

    $.ajax( "/greedy",
	({type: "POST",
	    data: $.toJSON({ "buy": purchases, "sell": sales, "recipient": email }),
	    contentType: "application/json",
        dataType: "json",
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


// If less than two decimal places, correct value. If more than two decimal places, do nothing.
function decimalCorrection(price){
	decimal = price.toString().split(".")[1];
	if(decimal == null){
		price = price.toFixed(2);
	}else if(decimal.length < 2){
		price = price.toFixed(2);
	}
	return price;
}

// Prints output and switches to HTML Output tab
function printOutput(data){
	
    var pairs, pair, buy, sell, count;
    table = document.getElementById("pairings");
    $("#pairings tr:gt(0)").remove();
    var pairingsRow = 0;
    var maxprofit = 0;

    pairs = data["pairs"]

    for(var pairIdx in pairs){
    	pair = pairs[pairIdx];
        buy = pair["buy"];
        sell = pair["sell"];
    	
    	pairingsRow++;
		row = table.insertRow(pairingsRow);
		cell = row.insertCell(0);
		cell.innerHTML = buy["month"] + '/' + buy["day"] + '/' + buy["year"];
		cell.className = 'col-md-1';
		cell = row.insertCell(1);
		cell.innerHTML = '$' + decimalCorrection(buy["price"]);
		cell.className = 'col-md-1';
		cell = row.insertCell(2);
		cell.innerHTML = sell["month"] + '/' + sell["day"] + '/' + sell["year"];
		cell.className = 'col-md-1';
		cell = row.insertCell(3);
		cell.innerHTML = '$' + decimalCorrection(sell["price"]);
		cell.className = 'col-md-1';
		cell = row.insertCell(4);
		cell.innerHTML = pair["count"];
		cell.className = 'col-md-1';
		cell = row.insertCell(5);
		var profit = pair["count"]*sell["price"] - pair["count"]*buy["price"];
		cell.innerHTML = '$' + decimalCorrection(profit);
		cell.className = 'col-md-1';
		maxprofit += profit;
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
    cell.innerHTML = '$' + decimalCorrection(maxprofit);
    
    // <form action="save.php" method="post" id="save"><input type="submit" class="btn btn-default col-md-6" value="Save Data"></form>
}

// Takes month, year and CIK parameters for SEC database pull
function pullSEC(){
    secStartYear = $("#secStartYear").val();
    secStartMonth = $("#secStartMonth").val();
    secEndYear = $("#secEndYear").val();
    secEndMonth = $("#secEndMonth").val();

    secCIK = $("#secCIK").val();
    
    secJSON = '{ "startYear":'+secStartYear+',"startMonth":'+secStartMonth+',"endYear":'+secEndYear+',"endMonth":'+secEndMonth+',"cik": "'+secCIK+'"}';

    $.ajax( "/pullSEC",
        ({type: "POST",
        data: secJSON,
        contentType: "application/json",
        dataType: "json",
        success: populate,
        error: function(data) {
            document.open();
            document.write(data.responseText);
            document.close();
        }
    }))
}

// Takes predetermined example data and populates Acquisitions and Disposals tables
function populateWithExample() {
    $("#purchases tr:gt(0)").remove();
    $("#sales tr:gt(0)").remove();
    
    var purchaseTable = $("#purchases")[0]
    var salesTable = $("#sales")[0]

	// Example data
    buyNumber = [1000, 2000, 800, 1000, 1000];
    buyPrice = [9,8,7,6,1];
    buyYear = [2014,2014,2014,2014,2012];
    buyMonth = [1,3,5,9,3];
    buyDay = [1,1,1,1,31];

    for (i = 0; i < buyNumber.length; i++) {
        row = insertPSRow(purchaseTable);
        $('#day', row).val(buyDay[i]);
        $('#month', row).val(buyMonth[i]);
        $('#year', row).val(buyYear[i]);
        $('#shares', row).val(buyNumber[i]);
        $('#value', row).val(buyPrice[i]);        
    }

    sellNumber = [400,1200,2400,1000,1000,1000,1000];
    sellPrice = [8,10,9,2,3,4,5];
    sellYear = [2014,2014,2014,2012,2012,2012,2012];
    sellMonth = [2,6,10,9,9,9,10];
    sellDay = [15,15,15,28,29,30,1];

    for (i = 0; i < sellNumber.length; i++) {
        row = insertPSRow(salesTable);
        $('#day', row).val(sellDay[i]);
        $('#month', row).val(sellMonth[i]);
        $('#year', row).val(sellYear[i]);
        $('#shares', row).val(sellNumber[i]);
        $('#value', row).val(sellPrice[i]);        
    }
}

// Format URL with HTML link
function insertFilingURL(url){
	return '<a href="'+ url +'" class="btn btn-default btn-xs" target="_blank">Link to filing</a>';
}

// Takes SEC data and populates Acquisitions and Disposals tables
function populate(data){
    $('#myTabs li:eq(0) a').tab('show');

    $("#purchases tr:gt(0)").remove();
    $("#sales tr:gt(0)").remove();
    
    var buys = data["buys"];
    var purchaseTable = $("#purchases")[0]

    for (tradeIdx in buys) {
        trade = buys[tradeIdx];

        row = insertPSRow(purchaseTable)
        $('#day', row).val(trade["day"]);
        $('#month', row).val(trade["month"]);
        $('#year', row).val(trade["year"]);
        $('#shares', row).val(trade["number"]);
        $('#value', row).val(trade["price"]);
        $('#title', row).append(trade["securityTitle"]);
        $('#ownership', row).append(trade["directOrIndirectOwnership"]);
        $('#filing', row).append(insertFilingURL(trade["filingURL"]));
    }
    var sells = data["sells"];
    var salesTable = $("#sales")[0]

    for (var tradeIdx in sells) {
        trade = sells[tradeIdx];

        row = insertPSRow(salesTable)
        $('#day', row).val(trade["day"]);
        $('#month', row).val(trade["month"]);
        $('#year', row).val(trade["year"]);
        $('#shares', row).val(trade["number"]);
        $('#value', row).val(trade["price"]);
        $('#title', row).append(trade["securityTitle"]);
        $('#ownership', row).append(trade["directOrIndirectOwnership"]);
        $('#filing', row).append(insertFilingURL(trade["filingURL"]));
    }
}
