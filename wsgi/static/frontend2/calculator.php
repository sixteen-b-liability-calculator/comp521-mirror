<?php
session_start();

$servername = "localhost";
$username = "root";
$password = "root";

$db="16bliabilitydatabase"; 
$tbl="users";
$connect = mysqli_connect($servername, $username, $password, $db);
?>
<html>
	<head>
		<!-- CSS -->
		<link rel="stylesheet" type="text/css" href="style.css">
		<link href="css/bootstrap.min.css" rel="stylesheet">
		<link href="css/datepicker.css" rel="stylesheet">
		<link rel="stylesheet" href="css/font-awesome.min.css">
		<link href="css/dropzone.css" type="text/css" rel="stylesheet" />
		
		<! Javascript -->
		<script src="js/dropzone.js"></script>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
		<script src="js/bootstrap.min.js"></script>
		<script src="main.js"></script>
	</head>
	<body onload="firstLoad()">
		<!-- Nav tabs -->
		<ul id="myTabs" class="nav nav-tabs" role="tablist">
			<li role="presentation"><a href="#account" role="tab" data-toggle="tab">
			<?php 
				if(isset($_SESSION['userid'])){ 
					echo "Hello " . $_SESSION['username'];
				} else{ echo "Login"; } ?></a></li>
			<li role="presentation" class="active"><a href="#input" role="tab" data-toggle="tab">Input</a></li>
			<li role="presentation"><a href="#output" role="tab" data-toggle="tab">Output</a></li>
			<li role="presentation"><a href="#fileupload" role="tab" data-toggle="tab">Upload (.cvs)</a></li>
		</ul>
		
		<!-- Beginning of tab pane -->
		<div class="tab-content">
		
		<!-- tab 0 "account" -->
		<div role="tabpanel" class="tab-pane fade" id="account">
			<div class="cornerindent">
				<?php
					if(!isset($_SESSION['userid'])){ 
				?>
						<form action="login.php" method="post" id="login">
							<div class="input-group">
								<input type="text" name="username" id="username" placeholder="username" class="form-control">
								<input type="password" name="password" id="password" placeholder="password" class="form-control">
								<input type="submit" class="btn btn-default col-md-6" value="Login"><button type="button" class="btn btn-default col-md-6">Register</button>
							</div>
						</form>
				<?php
					}
					else { ?>
						<form action="logout.php" method="post" id="logout">
							<div class="input-group">
								<input type="submit" class="btn btn-default" value="Logout">
							</div>
						</form>
						Saved Calculations
						<!--
<table id="calculations" class="form-group">
							<?php
								$userid =  $_SESSION['userid'];
								$query = "SELECT * FROM saved WHERE userid='$userid'";
								$result = $connect->query($query);
								$number = 0;
								while($row = $result->fetch_array()){
									?>
									<table class="form-group">
										<tr>
											<td class="theader">Buy Date</td>
											<td class="theader">Expense</td>
											<td class="theader">Sell Date</td>
											<td class="theader">Revenue</td>
											<td class="theader">Shares</td>
											<td class="theader">Profit</td>
										</tr>
									</table>
									<script type="text/javascript">
										returnToTable()
									</script>
									<div class="saved"><?php echo $row[1]; ?></div>
									<?php
								}
							?>
						</table>
-->
				<?php
					} 
				?>
			</div>
		</div>
		
		<!-- tab 1 "input" -->
		<div role="tabpanel" class="tab-pane fade in active" id="input">
			<div class="indent">
				<h2>Purchases</h2>
				<div class="indent shrink">
					<table id="purchases" class="form-group">
						<tr>
							<td class="theader">Day</strong></td>
							<td class="theader">Month</td>
							<td class="theader">Year</td>
							<td class="theader"># Shares</td>
							<td class="theader">Expense</td>
						</tr>
					</table>
				</div>
	
				<h2>Sales</h2>
				<div class="indent shrink">
					<table id="sales" class="form-group">
						<tr>
							<td class="theader">Day</td>
							<td class="theader">Month</td>
							<td class="theader">Year</td>
							<td class="theader"># Shares</td>
							<td class="theader">Revenue</td>
						</tr>
					</table>
				</div>
				<a href="#" class="btn btn-default" onclick="inputToJSON()">Compute</a>
			</div>
		</div>
		
		<!-- tab 2 "output" -->
		<div role="tabpanel" class="tab-pane fade" id="output">
			<div class="cornerindent shrink">
				<table id="pairings">
					<tr>
						<td class="theader">Buy Date</td>
						<td class="theader">Expense</td>
						<td class="theader">Sell Date</td>
						<td class="theader">Revenue</td>
						<td class="theader">Shares</td>
						<td class="theader">Profit</td>
					</tr>
				</table>
				<div id="save">
					<?php
						if(isset($_SESSION['userid'])){ 
					?>
					<button type="button" class="btn btn-default col-md-6" onclick="save()">Save Data</button>
					<?php
						}
					?>
				</div>
			</div>
		</div>
		
		<!-- tab 3 "file upload" -->
		<div role="tabpanel" class="tab-pane fade" id="fileupload">
			<form action="upload.php" class="dropzone"></form>
			<div id="dropzoneID"></div>
		</div>
		
		<!-- Ending of tab pane -->
		
	</body>
</html>
