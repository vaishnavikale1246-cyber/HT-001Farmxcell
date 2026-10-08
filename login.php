<?php

session_start();

$conn = new mysqli("localhost","root","","agrihelper");

if($conn->connect_error){
die("Database connection failed");
}

$email = $_POST['email'];
$password = $_POST['password'];

$sql = "SELECT * FROM users WHERE email='$email' AND password='$password'";

$result = $conn->query($sql);

if($result->num_rows > 0){

$user = $result->fetch_assoc();

$_SESSION['user_id'] = $user['id'];
$_SESSION['role'] = $user['role'];

if($user['role']=="admin"){

header("Location: admin/dashboard.php");

}else{

header("Location: index.php");

}

}else{

echo "Invalid Email or Password";

}

$conn->close();

?>