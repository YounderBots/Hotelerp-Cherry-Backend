import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// import Playground from './Playground'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
    {/* <Playground /> */}
  </StrictMode>,
)
