<?php
// Database connection
$conn = new mysqli("localhost", "root", "", "agrihelper");

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get form data
$email = $_POST['email'];
$password = $_POST['password'];

// Check user in database
$sql = "SELECT * FROM users WHERE email='$email' AND password='$password'";
$result = $conn->query($sql);

// Login check
if ($result->num_rows > 0) {
    echo "<h2>Login Successful ✅</h2>";
} else {
    echo "<h2>Invalid Email or Password ❌</h2>";
}

$conn->close();
?>