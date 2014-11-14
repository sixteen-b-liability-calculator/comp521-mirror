<?php
session_start();

$servername = "localhost";
$username = "root";
$password = "root";

$db="16bliabilitydatabase"; 
$tbl="users";
$connect = mysqli_connect($servername, $username, $password, $db);

if (is_ajax()) {
  $return = $_POST;
  $userid = $_SESSION['userid'];
  ob_start();
  var_dump($return);
  $result = ob_get_clean();
  $string = mysqli_real_escape_string($connect, $result);
  $query = "INSERT INTO saved (userid, json) VALUES ('$userid', '$string')";
  mysqli_query($connect, $query);
}

//Function to check if the request is an AJAX request
function is_ajax() {
  return isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) == 'xmlhttprequest';
}
?>