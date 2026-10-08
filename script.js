let users = [];

function showRegister(){
document.getElementById("loginForm").style.display="none";
document.getElementById("registerForm").style.display="block";
}

function showLogin(){
document.getElementById("loginForm").style.display="block";
document.getElementById("registerForm").style.display="none";
}

document.getElementById("registerForm").addEventListener("submit",function(e){

e.preventDefault();

let username=document.getElementById("regUsername").value;
let password=document.getElementById("regPassword").value;
let role=document.getElementById("regRole").value;

users.push({username,password,role});

alert("Registration Successful");

showLogin();

});

document.getElementById("loginForm").addEventListener("submit",function(e){

e.preventDefault();

let username=document.getElementById("loginUsername").value;
let password=document.getElementById("loginPassword").value;
let role=document.getElementById("role").value;

let user=users.find(u=>u.username===username && u.password===password && u.role===role);

if(user){

if(role==="admin"){
alert("Admin Login Success");
window.location="admin.html";
}else{
alert("User Login Success");
window.location="user.html";
}

}else{
alert("Invalid Login");
}

});