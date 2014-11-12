<?php
session_start();

$servername = "localhost";
$username = "root";
$password = "root";

$db="16bliabilitydatabase"; 
$tbl="users";
$connect = mysqli_connect($servername, $username, $password, $db);

$username=$_POST['username']; 
$password=$_POST['password']; 

$username = stripslashes($username);
$password = stripslashes($password);
$username = mysqli_real_escape_string($connect, $username);
$password = md5(mysqli_real_escape_string($connect, $password));
$query = "SELECT * FROM users WHERE username='$username' AND password='$password'";
$result = $connect->query($query);
$row = $result->fetch_array();

if($username == $row[1] && $password == $row[2]){
	$_SESSION['userid'] = $row[0];
	$_SESSION['username'] = $username;
}

header("location:calculator.php");

?>