import React from 'react';
import tpLogo from '../../assets/layout/Cherry.png';
import './LogoLoaderComponent.css'; // import the css
 
const LogoLoaderComponent = () => {
  return (
    <div className="logo-loader-container">
      {/* Logo loader */}
      <img src={tpLogo} alt="Cherry" className="logo-loader-img" />
      {/* <div className="logo-loader-text">Loading...</div> */}
    </div>
  );
};
 
export default LogoLoaderComponent;