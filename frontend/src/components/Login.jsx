import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';
import "./UnlockMira.css";

function Login({ onLogin }) { // Add onLogin prop
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState(''); // To store and display error messages
  const clearFields = () => {
    setEmail('');
    setPassword('');
  };
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const response = await fetch("http://localhost:8000/login/", {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({  
              username: email, // assuming username is the email for login
              password: password
          })
      });
      console.log('Response:', response);
      const data = await response.json();
      console.log('Data:', data);

      
      if(response.ok) {
          // Clear the fields
          setEmail('');
          setPassword('');
          // Store the token and navigate the user
          localStorage.setItem('token', data.token);
          onLogin && onLogin(); // Call onLogin prop if defined
          navigate('/Dashboard');        
      } else {
          // Handle errors and display an error message
          setErrorMessage(data.detail || 'An error occurred.');
      }
    } catch (error) {
      // Handle any unexpected errors
      setErrorMessage('An unexpected error occurred. Please try again.');
    }
  };
  return (
      <div className="card card-login">
        <div className="card-header">
          <h3 className="title-up text-center">Login</h3>
        </div>
        <div className="card-body">
        {errorMessage && <div className="error-message">{errorMessage}</div>}
          <form action="" className="form" method="">
            <div className="field input-group">
              <input
                className="input-field"
                placeholder="Email"
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="field input-group">
              <input
                className="input-field"
                placeholder="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </form>
        </div>
        <div className="card-footer">
          <button className="button1" onClick={handleLogin}>
            Login
          </button>
          <button className="button2" onClick={clearFields}>Clear</button>
        </div>
        </div>
  );
}
export default Login;
  
