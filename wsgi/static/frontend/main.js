var defaultInputCount = 10;
var undo_p_stack = [];
var undo_s_stack = [];
var total_purchases_entered = 0;
var total_sales_entered = 0;
var data_table;

// on initial page load, pull data into DataTables
// test
$(document).ready( function () {
    $.ajax({
        url: "/queryDB",
        type: "GET",
        success: function(result) {
            myData = $.map(result['data'], function(el) {
                return [[el.cik, el.name, el.lp, el.date, el.url]];
            });
            // console.log("myData: " + myData);
            // initalize data table
            data_table = $('#data_table').DataTable({
                paging: true,
                // scrollY: 400,
                dataPageLength: 25,
                data: myData,
                "order": [[ 0, 'asc' ]],
                "oLanguage": {
                    "sEmptyTable":     "No data available for selected date"
                },
                columns: [
                    { title: "CIK" },
                    { title: "Name" },
                    { title: "LP liability",
                        "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                            $(nTd).click(function() {
                                var end = oData[3];
                                var endDate = new Date(end);
                                endDate.setDate(endDate.getDate()+1);
                                console.log("endDate: " + endDate);

                                var startDate = new Date();
                                startDate.setYear(endDate.getYear()-1);
                                startDate.setMonth(endDate.getMonth()-6);
                                startDate.setDate(startDate.getDate()-3);
                                console.log(startDate);
                                // console.log(oData[0]);
                                // var endDate = new Date();
                                // endDate.setYear(1900+endDate.getYear());
                                // var endYear = parseDate(endDate, "y");
                                // var endMonth = parseDate(endDate, "m");
                                // console.log("endDate: " + endDate);
                                // console.log("endYear: " + endYear+1900);
                                console.log("endYear2: " + endDate.getYear()+1900);
                                console.log("endMonth2: " + endDate.getMonth());

                                var startDate = new Date();
                                startDate.setYear(1900+startDate.getYear()-2);  // subtract 2 years
                                startDate.setMonth(startDate.getMonth()-6);     // subtract 6 months
                                startDate.setDate(startDate.getDate()-3);       // subtract 3 days (for Jammies)
                                var startYear = parseDate(endDate, "y");
                                var startMonth = parseDate(endDate, "m");

                                var secJSON = '{ "startYear":'+startYear+',"startMonth":'+startMonth+',"endYear":'+endYear+',"endMonth":'+endMonth+',"cik": "'+1194358+'"}';

                                console.log("secJSON: " + secJSON);
                                // if (secCIK && secCIK != "") {
                                //     $.ajax( "/pullSEC",
                                //         ({type: "POST",
                                //         data: secJSON,
                                //         contentType: "application/json",
                                //         dataType: "json",
                                //         success: [populate, removeMessage],
                                //         error: function(data) {
                                //             document.open();
                                //             document.write(data.responseText);
                                //             document.close();
                                //         }
                                //     }));
                                // }
                            });
                        }
                    },
                    { title: "Date of most recent form" },
                    { title: "Link to most recent form",
                        "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                            $(nTd).html("<a href='"+oData[4]+"' target='_blank'>Link to filing</a>");
                        }
                    }
                ],
            });
            // $('#data_table tbody').on('click', 'td', function () {
            //     console.log(data_table.row(this).data());
            // });
        },
        error: function(error) {
            console.log("fail: " + error);
        }
    });
} );

function test() {
    console.log("new testing");
}

// Called by <body> onload
function firstLoad(){
    createDefaultInputRows();

    // Sets the Edgar Date range for selecting from the database.
    $('#secEndDate').datepicker("setDate",'0');
    $('#secStartDate').datepicker("setDate",setStartDate());

    // Sets yesterday as the default search date
    $('#searchDate').datepicker("setDate", -1);

    // Sets the Event listener for the CSV upload.
    $("#csv-file").change(populateWithCSVFile);
}

function setStartDate(){
    var date = new Date();
    // Subtract 2 years
    date.setYear(1900+date.getYear()-2);
    //subtract 6 months
    date.setMonth(date.getMonth()-6);
    // TODO:valakuzhy
    // Jammies allow for subtracting up to three days.
    // Will need something more sophisticated to get this completed right though
    date.setDate(date.getDate()-3);
    return date;
}

// Removes row of data
function removePSRow(button){

    var delete_ps_row_id = button.parentElement.parentElement.id;

    var undo_row = [];
    var undo_stack;

    // check if deleted row is in Purchases or Sales
    if (delete_ps_row_id.substring(0,1) == "p") {
        undo_stack = undo_p_stack;
        document.getElementById('undo-purchases').disabled = false;
    }
    else {
        undo_stack = undo_s_stack;
        document.getElementById('undo-sales').disabled = false;
    }

    // store the row's values in the appropriate stack
    var count = 0;
    $("#" + delete_ps_row_id + " td").each(function( i ) {
        $("input", this).each(function(j) {
            console.log(this.value);
            if (count > 0) undo_row[count-1] = this.value;
            count++;
        });
    });
    $("#" + delete_ps_row_id + " td").each(function( i ) {
        console.log("******");
        $("div", this).each(function(j) {
            undo_row[count-1] = this;
            console.log(this);
            count++;
        });
    });


    undo_stack.push(undo_row);

    // remove the row
    button.parentElement.parentElement.remove();
}

// Undo row removal (purchases or sales table)
function undoRowRemoval(table_name){
    var removed_row;
    // if removed row was part of Purchases table
    if (table_name == "purchases") {
        removed_row = undo_p_stack.pop();
        purchaseRow();

        // store references to new row
        var new_p_row_id = "p_row_" + (total_purchases_entered-1);
        var new_p_row = document.getElementById(new_p_row_id);

        var count = 0;

        // populate new row with date/quantity/price
        $("#" + new_p_row_id + " td").each(function( i ) {
            $("input", this).each(function(j) {
                if (count > 0) this.value = removed_row[count-1];
                count++;
            });
        });

        // populate new row with title/ownership/filing link (if applicable)
        $('#title', new_p_row).append(removed_row[count-1].innerHTML);
        count++;
        $('#ownership', new_p_row).append(removed_row[count-1].innerHTML);
        count++;
        $('#filing', new_p_row).append(removed_row[count-1].innerHTML);
        count++;

        // disable undo button if stack is empty
        if (undo_p_stack.length == 0) {
            document.getElementById('undo-purchases').disabled = true;
        }
    }
    // if removed row was part of Sales table
    if (table_name == "sales") {
        removed_row = undo_s_stack.pop();
        saleRow();

        // store references to new row
        var new_s_row_id = "s_row_" + (total_sales_entered-1);
        var new_s_row = document.getElementById(new_s_row_id);

        var count = 0;
        // populate new row with date/quantity/price
        $("#" + new_s_row_id + " td").each(function( i ) {
            $("input", this).each(function(j) {
                if (count > 0) this.value = removed_row[count-1];
                count++;
            });
        });

        // populate new row with title/ownership/filing link (if applicable)
        $('#title', new_s_row).append(removed_row[count-1].innerHTML);
        count++;
        $('#ownership', new_s_row).append(removed_row[count-1].innerHTML);
        count++;
        $('#filing', new_s_row).append(removed_row[count-1].innerHTML);
        count++;

        // disable undo button if stack is empty
        if (undo_s_stack.length == 0) {
            document.getElementById('undo-sales').disabled = true;
        }
    }
}


// Inserts empty row for acquisitions or disposal table
function insertPSRow(table){
    var row = table.insertRow();

    // assign an id to the new row
    var table_id = table.id;
    if (table_id == "purchases") {
        var num_P_rows = total_purchases_entered
        total_purchases_entered++;
        row.id = "p_row_" + num_P_rows;
    }
    else if (table_id == "sales") {
        var num_S_rows = total_sales_entered;
        total_sales_entered++;
        row.id = "s_row_" + num_S_rows;
    }

    // assign cells to the new row
    var cell = row.insertCell();
    cell.innerHTML = '<input type="button" id="remove" value="Remove" class="btn btn-default btn-xs" onClick="removePSRow(this);">';

    cell = row.insertCell();
    cell.innerHTML = '<input type="text" size="9" class="datepicker">';
    $(".datepicker").datepicker();

    cell = row.insertCell();
    cell.innerHTML = '<input type="text" id="shares" size=12 class="form-control">';
    $('#shares',row)[0].onchange = checkIfNonnegativeOnChange;

    cell = row.insertCell();
    cell.innerHTML = '<input type="text" id="value" size =14 class="value form-control">';
    $('#value',row)[0].onchange = checkIfNonnegativeOnChange;

    cell = row.insertCell();
    cell.innerHTML = '<div id="title"></div>';

    cell = row.insertCell();
    cell.innerHTML = '<div id="ownership"></div>';

    cell = row.insertCell();
    cell.innerHTML = '<div id="filing"></div>'
    row.onchange = checkIfMissingValue;

    return row;
}

// For use when adding rows to check whether there is an error when new values are included.
// Applies a "inputDataError" class on these elements.
function checkIfNonnegativeOnChange() {
    console.log($(this));
    if ($(this).val() > 0 || $(this).val() == "") {
        $(this).removeClass("inputDataError");
        $(this).removeClass("inputDataWarning");
        $(this).removeClass("zeroValue");
    } else if ($(this).val() < 0) {
        $(this).addClass("inputDataError");
    } else if ($(this).val() == 0) {
        $(this).addClass("inputDataWarning");
        $(this).addClass("zeroValue");
    }
}

// Checks to see if there are partially filled rows.
// Applies a "inputDataWarning" class on these rows.
function checkIfMissingValue() {
    var row = $(this);

    // The three values you must check are: date, value, and shares
    var valueHasVal = $('#value', row).val() != "";
    var sharesHasVal = $('#shares', row).val() != "";
    var dateHasVal = $('.datepicker', row).val() != "";

    var isFilledRow = valueHasVal && sharesHasVal && dateHasVal;
    var isEmptyRow = !(valueHasVal || sharesHasVal || dateHasVal);

    if (isFilledRow || isEmptyRow) {
        row.removeClass("inputDataWarning");
    } else {
        row.addClass("inputDataWarning");
    }
}

// Download data from text box
function downloadCSV() {
    data = $('#csv-data')[0].value;
    $("#saveCSV").attr('href','data:text/csv;charset=utf8,' + encodeURIComponent(data))
}

function createDefaultInputRows() {
    var purchases = $("#purchases")[0];
    var sales = $("#sales")[0];
    for(i = 0; i < defaultInputCount; ++i){
    	insertPSRow(purchases);
    	insertPSRow(sales);
    }
}

// Called by "Clear Input" button
function clearInputContent() {
    clearInputTab();
    createDefaultInputRows();
}

// Used in Undo Row Removal (adds a single purchase row)
function purchaseRow() {
    purchases = $("#purchases")[0];
    insertPSRow(purchases);
}

// Called by "Add Row" button for Acquisitions table
function purchaseRows(){
    numrows = parseInt($("#addPurchases").val());
    purchases = $("#purchases")[0];
    for (i = 0; i < numrows; i++) {
        insertPSRow(purchases);
    }
}

// Used in Undo Row Removal (adds a single sale row)
function saleRow() {
    sales = $("#sales")[0];
    insertPSRow(sales);
}

// Called by "Add Row" button for Disposals table
function saleRows(){
    numrows = parseInt($("#addSales").val());
    sales = $("#sales")[0];
    for (i = 0; i < numrows; i++) {
        insertPSRow(sales);
    }
}
// Testing
// Called in inputToJSON() to store living input data
function readTable(table){
    out = []
    var elt;
    for (var i = 1; i < table.rows.length; i++) {
        var row = table.rows[i];

        // Do not include rows that have warnings in them.
        if (row.className.indexOf("inputDataWarning") > -1) continue;

    	elt = new Object();
    	elt.price = parseFloat($("#value", row).val());
        var date = $(".datepicker", row).val();
    	elt.month = parseDate(date, "m");
        elt.day = parseDate(date, "d")
    	elt.year = parseDate(date, "y");
    	elt.number = parseFloat($("#shares", row).val());
    	if(!isNaN(elt.price)){
    	    out.push(elt);
    	}
    }
    return out;
}

// Calculates max profit with linear programming or LIHO
function inputToJSON(url){

    if (inputHasErrors()) return;
    if (!ignoreWarnings()) return;

    var purchases = readTable($("#purchases")[0]);
    var sales = readTable($("#sales")[0]);

    //var email = $("#email").val();

    var stella = $('#correction-stella')[0].checked;
    var jammies = $('#correction-jammies')[0].checked;
    if (jammies) {
        stella = true;  // Since jammies implies stella.
    }

    // clear output tab, disable "Download Output" button
    $("#pairings tr:gt(0)").remove();
    $("#pairings").append("<h3 id=\"computing\">Computing Result...</h3>")
    document.getElementById("downloadOutput").disabled = true;


    $.ajax( url,
	({type: "POST",
	    //data: $.toJSON({ "buy": purchases, "sell": sales, "stella_correction": stella, "jammies_correction": jammies, "recipient": email }),
        data: $.toJSON({ "buys": purchases, "sells": sales, "stella_correction": stella, "jammies_correction": jammies}),
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
    $('#tabs').tabs('option','active',1);
}

function inputHasErrors() {
    var errors = $('.inputDataError');
    if (errors.length == 0) return false;
    if (errors.length == 1 ) {
        alert("There is an error in the input. Unable to continue computation");
    } else {
        alert("There are "+ errors.length +" errors in the input. Unable to continue computation");
    }
    return true;
}

// Returns true if you want to ignore all warnings that have appeared.
function ignoreWarnings() {
    var warnings = $('.inputDataWarning');
    if (warnings.length == 0) return true;
    if (warnings.length == 1) return confirm("1 row has missing or zero-valued data and will be excluded from the computation.  Would you like to continue?");
    return confirm(warnings.length+" rows have missing or zero-valued data and will be excluded from the computation.  Would you like to continue?");
}

// If less than two decimal places, correct value. If more than two decimal places, round to four decimal places.
function decimalCorrection(price){
	var decimal = price.toString().split(".")[1];
    var price;
	if(decimal == null){
		price = price.toFixed(2);
	}else if(decimal.length < 2){
		price = price.toFixed(2);
	}
    else if (decimal.length > 2) {
        price = price.toFixed(4);
    }
	return price;
}

// Prints output and switches to HTML Output tab
function printOutput(data){
    var pairs, pair, buy, sell, count, table, cell, profit;
    table = document.getElementById("pairings");
    $("#pairings tr:gt(0)").remove();
    var pairingsRow = 0;
    var maxprofit = 0;

    pairs = data["pairs"]

    // remove "Calculating Result..." now that results have been calculated
    $("#computing").remove();
    // enable Download Output button
    document.getElementById("downloadOutput").disabled = false;

    for(var pairIdx in pairs){
    	var pair = pairs[pairIdx];
        var buy = pair["buy"];
        var sell = pair["sell"];

    	pairingsRow++;
		row = table.insertRow(pairingsRow);
		cell = row.insertCell(0);
		cell.innerHTML = buy["month"] + '/' + buy["day"] + '/' + buy["year"];
		cell = row.insertCell(1);
		cell.innerHTML = '$' + decimalCorrection(buy["price"]);
		cell = row.insertCell(2);
		cell.innerHTML = sell["month"] + '/' + sell["day"] + '/' + sell["year"];
		cell = row.insertCell(3);
		cell.innerHTML = '$' + decimalCorrection(sell["price"]);
		cell = row.insertCell(4);
		cell.innerHTML = pair["count"];
		cell = row.insertCell(5);
		profit = pair["count"]*sell["price"] - pair["count"]*buy["price"];
		cell.innerHTML = '$' + decimalCorrection(profit);
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

// Alert the user that EDGAR search is happening
function searchMessage() {
    $(".searchButton").append("<h3 id=\"searching\">Searching EDGAR database... This may take a couple minutes.</h3>");
}

function removeMessage() {
    $("#searching").remove();
}

// Takes month, year and CIK parameters for SEC database pull
function pullSEC(){
    var startDate = $("#secStartDate").val();
    var secStartYear = parseDate(startDate, "y");
    var secStartMonth = parseDate(startDate, "m");

    var endDate = $("#secEndDate").val();

    var secEndYear = parseDate(endDate, "y");
    var secEndMonth = parseDate(endDate, "m");

    var secCIK = $("#secCIK").val();

    var secJSON = '{ "startYear":'+secStartYear+',"startMonth":'+secStartMonth+',"endYear":'+secEndYear+',"endMonth":'+secEndMonth+',"cik": "'+secCIK+'"}';

    if (secCIK && secCIK != "") {
        $.ajax( "/pullSEC",
            ({type: "POST",
            data: secJSON,
            contentType: "application/json",
            dataType: "json",
            success: [populate, removeMessage],
            error: function(data) {
                document.open();
                document.write(data.responseText);
                document.close();
            }
        }));
    }
}

// Query SEC database for given row's CIK
// use today as end date and 2.5 yrs and 3 days ago as default start date (using Jammies)
function tableLiability(cik) {

    var endDate = new Date();
    var endYear = parseDate(endDate, "y");
    var endMonth = parseDate(endDate, "m");

    var startDate = new Date();
    startDate.setYear(1900+startDate.getYear()-2);  // subtract 2 years
    startDate.setMonth(startDate.getMonth()-6);     // subtract 6 months
    startDate.setDate(startDate.getDate()-3);       // subtract 3 days (for Jammies)
    var startYear = parseDate(endDate, "y");
    var startMonth = parseDate(endDate, "m");

    var secJSON = '{ "startYear":'+startYear+',"startMonth":'+startMonth+',"endYear":'+endYear+',"endMonth":'+endMonth+',"cik": "'+cik+'"}';


    if (secCIK && secCIK != "") {
        $.ajax( "/pullSEC",
            ({type: "POST",
            data: secJSON,
            contentType: "application/json",
            dataType: "json",
            success: [populate, removeMessage],
            error: function(data) {
                document.open();
                document.write(data.responseText);
                document.close();
            }
        }));
    }
}


// proof-of-concept for Daily Report. Pulls CIKs for daily Form 4 filings.
function pullDailyReport() {
    $.ajax( "/pullDailyReport",
        ({type: "GET",
        contentType: "application/json",
        dataType: "json",
        success: [displayReport, removeMessage],
        error: function(data) {
            document.open();
            document.write(data.responseText);
            document.close();
        }
    }));
}

function displayReport(data) {
    var filings = data["filings"];
    var report = "Report:";
    for (var idx in filings) {
        var f = filings[idx];
        report += "\n" + f["cik"] + ", " + f["name"] + ", " + f["url"] + ", "
                    + f["liability"] + ", "+ f["lastfiling"];
    }
    $('#report-data').val(report);
    removeMessage();
}

// Takes predetermined example data and populates Acquisitions and Disposals tables
function populateWithExample() {

    buyData = [];
    buyData.push({number: 1000, price:9, day:1, month:1, year:2014});
    buyData.push({number: 2000, price:8, day:1, month:3, year:2014});
    buyData.push({number: 800, price:7, day:1, month:5, year:2014});
    buyData.push({number: 1000, price:6, day:1, month:9, year:2014});
    buyData.push({number: 1000, price:1, day:31, month:3, year:2012});
    sellData = [];
    sellData.push({number: 400, price:8, day:15, month:2, year:2014});
    sellData.push({number: 1200, price:10, day:15, month:6, year:2014});
    sellData.push({number: 2400, price:9, day:15, month:10, year:2014});
    sellData.push({number: 1000, price:2, day:28, month:9, year:2012});
    sellData.push({number: 1000, price:3, day:29, month:9, year:2012});
    sellData.push({number: 1000, price:4, day:30, month:9, year:2012});
    sellData.push({number: 1000, price:5, day:1, month:10, year:2012});

    populate({buys: buyData, sells: sellData});
}

// Format URL with HTML link
function insertFilingURL(url){
	return '<a href="'+ url +'" class="btn btn-default btn-xs" target="_blank">Link to filing</a>';
}

function populateWithCSV() {
    var inputString = $('#csv-data').val();
    var jsonString = '{ "csvString":'+ inputString + ' }';

    // test comment
    $.ajax( "/populateWithCSV",
        ({type: "POST",
        data: inputString,
        contentType: "text/csv",
        dataType: "json",
        success: populate,
        error: function(data) {
            document.open();
            document.write(data.responseText);
            document.close();
        }
    }))
}

// Read in file, and place
function populateWithCSVFile(evt) {
    var f = evt.target.files[0];
    if (f) {
        var reader = new FileReader();
        reader.onload = function() {
            var text = reader.result;
            $('#csv-data').val(text);
            populateWithCSV();
        }
        reader.readAsText(f)
    } else {
        alert("Failed to load file");
    }
}

// Converts the input page into CSV and displays it on the CSV upload page.
function convertToCSV() {
    var purchaseTable = $('#purchases')[0].rows;
    var csvString = ""

// Skip the header line
    for (var i = 1; i< purchaseTable.length; i++) {
        var row = purchaseTable[i];
        var date = $('.datepicker', row)[0].value;
        var number = $('#shares', row)[0].value;
        var price = $('#value', row)[0].value;
        if (date == "" && price == "" && number == "") {
            // do nothing
        }
        else {
            csvString += date + ", " + price + ", " + number + ", buy\n"
        }    }

    var saleTable = $('#sales')[0].rows;
    for (var i = 1; i< saleTable.length; i++) {
        var row = saleTable[i];
        var date = $('.datepicker', row)[0].value;
        var number = $('#shares', row)[0].value;
        var price = $('#value', row)[0].value;
        if (date == "" && price == "" && number == "") {
            // do nothing
        }
        else {
            csvString += date + ", " + price + ", " + number + ", sell\n"
        }
    }
    $('#csv-data')[0].value = csvString;
    $('#tabs').tabs('option','active',2);
}

// Converts the output into CSV and automatically downloads it.
function downloadOutput() {

    var output = new Array();
    var outputRow;

    // store output in 2D array
    $("#pairings tr").each(function(i) {
        outputRow = new Array();
        $(this).find("td").each(function(i) {
            outputRow.push(this.innerHTML);
        });
        output.push(outputRow);
    });

    // format Header line and edit "Total"
    output[0] = ["Purchase Date", "Per Share Price", "Sale Date", "Per Share Price", "Paired Securities", "Profit"];
    output[output.length-1][4] = "Total";

    // create csv
    var csvContent = "";
    output.forEach(function(infoArray, index){
    dataString = infoArray.join(",");
    csvContent += index < output.length ? dataString+ "\n" : dataString;
    });

     $("#downloadOutput").attr('href','data:text/csv;charset=utf8,' + encodeURIComponent(csvContent))

}

// Takes JSON Data and populates Purchase and Sales tables
function populate(data){
    clearInputTab();
    $('#tabs').tabs('option','active',0);

    var buys = data["buys"];
    var purchaseTable = $("#purchases")[0]

    for (var tradeIdx in buys) {
        var trade = buys[tradeIdx];

        var row = insertPSRow(purchaseTable);
        var date = createDateString(trade["day"], trade["month"], trade["year"]);

        $('.datepicker', row).val(date);
        $('#shares', row).val(trade["number"]);
        $('#value', row).val(trade["price"]);
        $('#title', row).append(trade["securityTitle"]);
        $('#ownership', row).append(trade["directOrIndirectOwnership"]);
        if ("filingURL" in trade) {
            $('#filing', row).append(insertFilingURL(trade["filingURL"]));
        }
    }
    var sells = data["sells"];
    var salesTable = $("#sales")[0]

    for (var tradeIdx in sells) {
        var trade = sells[tradeIdx];

        var row = insertPSRow(salesTable);
        var date = createDateString(trade["day"], trade["month"], trade["year"]);

        $('.datepicker', row).val(date);
        $('#shares', row).val(trade["number"]);
        $('#value', row).val(trade["price"]);
        $('#title', row).append(trade["securityTitle"]);
        $('#ownership', row).append(trade["directOrIndirectOwnership"]);
        if ("filingURL" in trade) {
            $('#filing', row).append(insertFilingURL(trade["filingURL"]));
        }
    }
}

// Given the current implementation, dates are mm/dd/yyyy
function parseDate(dateString, d_m_y) {
    if (typeof dateString != 'string') {
        return;
    }
    var dateArray = dateString.split("/");
    if (d_m_y.indexOf("d") >= 0) {
        return parseInt(dateArray[1]);
    } else if (d_m_y.indexOf("m") >= 0) {
        return parseInt(dateArray[0]);
    } else {
        return parseInt(dateArray[2]);
    }
}

// Given the current implementation, dates are mm/dd/yyyy
function createDateString(day, month, year) {
    if (parseInt(month) > 12) {
        throw "Invalid month value " + month;
    }
    return month + "/" + day + "/" + year;
}

// Clears the input tab of all information
function clearInputTab() {
    $("#purchases tr:gt(0)").remove();
    $("#sales tr:gt(0)").remove();

    // reset row id's
    total_purchases_entered = 0;
    total_sales_entered = 0;
    // remove all entries from undo stack
    undo_p_stack = [];
    undo_s_stack = [];
    // disable undo buttons
    document.getElementById('undo-purchases').disabled = true;
    document.getElementById('undo-sales').disabled = true;

}

// test databse connection
function testDatabase() {
    // debug (test that form draws data correctly)
    console.log($('form').serialize());
    // send data through ajax calll
    $.ajax({
        url: "/testDB",
        data: $('form').serialize(),
        dataType: "text",
        type: "POST",
        success: function(result) {
            console.log(result);
            alert("success" + result);
            // alert(response);
        },
        error: function(error) {
            // console.log(error);
            alert("fail: " + error);
        }
    });
}

// query database
function queryDB() {
    // get data through ajax calll
    $.ajax({
        url: "/queryDB",
        type: "GET",
        success: function(result) {
            console.log(result);
            alert("success" + result);
        },
        error: function(error) {
            alert("fail: " + error);
        }
    });
}

// reload database with data for selected date
function refreshDB() {
    var searchDate = $("#searchDate").val();
    var searchYear = parseDate(searchDate, "y");
    var searchMonth = parseDate(searchDate, "m");
    var searchDay = parseDate(searchDate, "d");
    var searchArray = [searchYear, searchMonth, searchDay];
    // console.log("SEARCH ARRAY: " + searchArray);
    if (searchDate != "") {
        var myData;
        $(document).ready( function () {
            $.ajax({
                url: "/refreshDB",
                type: "POST",
                data: $('form').serialize(),
                success: function(result) {
                    // alert("success");
                    myData = $.map(result['data'], function(el) {
                        return [[el.cik, el.name, el.lp, el.date, el.url]];
                    });
                    var datatable = $('#data_table').dataTable().api();
                    datatable.clear();
                    datatable.rows.add(myData);
                    datatable.draw();
                },
                error: function(error) {
                    console.log("fail: " + error);
                }
            });
        } );
    }
}
