var defaultInputCount = 10;

function removePSRow(button){
    button.parentElement.parentElement.remove();
}

function insertPSRow(table){
    i = table.rows.length
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
    cell.className = 'col-md-6';
    
    cell = row.insertCell();
    cell.innerHTML = '<div id="filing"></div>'

    return row;
}

function insertFilingURL(url){
	return '<a href="'+ url +'" class="btn btn-default btn-xs">Link to filing</a>';
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

function readTable(table){
    out = []
    for(i = 1; i < table.rows.length; ++i){
	elt = {};
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

function inputToJSON(){
    purchases = readTable($("#purchases")[0]);
    sales = readTable($("#sales")[0]);
    
    email = $("#email").val()
    
    $.ajax( "/compute",
	({type: "POST",
	    data: $.toJSON({ "buy": purchases, "sell": sales, "recipient": email }),
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
    $("#pairings tr:gt(0)").remove();
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
        dataType: "json",
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

//  Clears the table from other values
    $("#purchases tr:gt(0)").remove();
    $("#sales tr:gt(0)").remove();
    
//  var beforeJSON = '{"buys":[{"day":11,"month":1,"number":2000,"price":44.1,"year":2007},{"day":11,"month":1,"number":1200,"price":44.39,"year":2007},{"day":11,"month":1,"number":3600,"price":44.76,"year":2007},{"day":11,"month":1,"number":2500,"price":45.04,"year":2007},{"day":11,"month":1,"number":700,"price":45.31,"year":2007},{"day":9,"month":2,"number":2000,"price":40.2,"year":2007},{"day":9,"month":2,"number":750,"price":40.6,"year":2007},{"day":23,"month":9,"number":15730,"price":54.84,"year":2006}],"sells":[{"day":11,"month":1,"number":10000,"price":34.585,"year":2007},{"day":9,"month":2,"number":5000,"price":3.125,"year":2007},{"day":9,"month":3,"number":5000,"price":2.5,"year":2007}]}';
    
    var month,day,year,number,price;
    
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
        $('#filing', row).append(insertFilingURL(trade["filingURL"]));
    }
}
