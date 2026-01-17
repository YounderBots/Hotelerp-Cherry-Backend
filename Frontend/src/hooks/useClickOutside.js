import { useEffect } from "react";

const useClickOutside = (ref, handler, when = true) => {
  useEffect(() => {


    
    if (!when) return;

    const listener = (event) => {
       
        
      // If ref is not set or click is inside → do nothing
      if (!ref.current || ref.current.contains(event.target)) return;

      handler(event);
    };

    document.addEventListener("mousedown", listener);
    document.addEventListener("touchstart", listener);

    return () => {
      document.removeEventListener("mousedown", listener);
      document.removeEventListener("touchstart", listener);
    };
  }, [ref, handler, when]);
};

export default useClickOutside;
