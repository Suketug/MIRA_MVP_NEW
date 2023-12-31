// Desc: Sign Up page for the application
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./UnlockMira.css";

function SignUp() {
  const [userType, setUserType] = useState('user');
  const [firstFocus] = React.useState(false);
  const [lastFocus] = React.useState(false);
  const [emailFocus] = React.useState(false);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [nmlsId, setNmlsId] = useState('');  // Only for Loan Officer
  const [errorMessage, setErrorMessage] = useState(''); // To store and display error messages
  const navigate = useNavigate();
  const clearFields = () => {
    setFirstName('');
    setLastName('');
    setUsername('');
    setPassword('');
    setConfirmPassword('');
    setNmlsId('');
  };

  const handleSignUp = async (event) => {
    event.preventDefault(); // Prevent the default form submission behavior
    if(password !== confirmPassword) {
      setErrorMessage('Passwords do not match.');
      return;
    }
    const userData = {
      username: email,  
      password: password,
      first_name: firstName,
      last_name: lastName,
      confirm_password: confirmPassword,
      role: userType === 'loanOfficer' ? 'Loan Officer' : 'Consumer'
    };
  
    if(userType === 'loanOfficer') {
      userData.nmlsId = nmlsId;  // Add NMLS ID for loan officers
    }
  
    const response = await fetch("http://localhost:8000/register/", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });
  
    const data = await response.json();

      if(response.ok) {
          // Clear the fields
          setFirstName('');
          setLastName('');
          setUsername('');
          setPassword('');
          setConfirmPassword('');
          setNmlsId('');
         // Navigate the user to login page or any other suitable page
         navigate('/Dashboard/chat-ui');

         const { access_token } = data;
         if (access_token) {
           sessionStorage.setItem('token', access_token);
         }
     
         // Clear the fields
         clearFields();
     
         // Navigate the user to the dashboard page or any other suitable page
         navigate('/Dashboard/chat-ui');
       } else {
         // Handle errors and display an error message
         setErrorMessage(data.detail || 'An error occurred during registration.');
       }
     }
     return (
      <div className="container">
        <div className="card card-signup">
          <div className="card-header">
            <nav className="nav-tabs-info justify-content-center">
              <button onClick={() => setUserType('user')} className={`nav-link ${userType === 'user' ? 'active' : ''}`}>User Login</button>
              <button onClick={() => setUserType('loanOfficer')} className={`nav-link ${userType === 'loanOfficer' ? 'active' : ''}`}>Loan Officer Login</button>
            </nav>
          </div>
          <form action="" className="form" onSubmit={handleSignUp}>
            <div className="card-body">
              <h3 id="heading" className="title-up text-center">Sign Up</h3>
            <div className="field input-group">
              <input
                className="input-field"
                placeholder="First Name"
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>
            <div className="field input-group">
              <input
                className="input-field"
                placeholder="Last Name"
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>
            <div className="field input-group">
              <input
                className="input-field"
                placeholder="Email"
                type="text"
                value={email}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            {userType === 'loanOfficer' && (
              <div className="field input-group">
                <input
                  className="input-field"
                  placeholder="NMLS ID"
                  type="text"
                  value={nmlsId}
                  onChange={(e) => setNmlsId(e.target.value)}
                />
              </div>
            )}
            <div className="field input-group">
              <input
                className="input-field"
                placeholder="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="field input-group">
              <input
                className="input-field"
                placeholder="Confirm Password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
          </div>
          <div className="card-footer">
            <button className="button1" type="submit">Get Started</button>
            <button className="button2" type="button" onClick={clearFields}>Clear</button> <br />
          </div>
        </form>
      </div>
    </div>
  );
}

export default SignUp;