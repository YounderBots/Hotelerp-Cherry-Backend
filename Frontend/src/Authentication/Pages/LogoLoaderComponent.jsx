import React from 'react';
import tpLogo from '../../assets/layout/Cherry.png';
import './LogoLoaderComponent.css'; // import the css

// Route-level loading state.
//
// WHY role="status" AND THE VISUALLY-HIDDEN TEXT
//   This is what every lazy route shows while its chunk loads, so it is the
//   only thing a screen reader hears during a navigation. As an image alone it
//   announced nothing: `alt="Cherry"` is read on some assistive tech and
//   ignored on others, and nothing said what was happening or that it would
//   end.
//
//   `role="status"` with `aria-live="polite"` announces the text when it
//   appears, without interrupting whatever the user is doing. The text is
//   visually hidden rather than hidden (`display:none` / `visibility:hidden`)
//   because those remove it from the accessibility tree as well -- which would
//   make it announce to nobody.
//
//   The label that used to sit under the logo is restored rather than only
//   hidden, so it is there for anyone whose CSS does not load and for a sighted
//   user on a slow connection.
const LogoLoaderComponent = () => {
  return (
    <div className="logo-loader-container" role="status" aria-live="polite">
      <img src={tpLogo} alt="" aria-hidden="true" className="logo-loader-img" />
      <p className="logo-loader-text">Loading…</p>
    </div>
  );
};

export default LogoLoaderComponent;