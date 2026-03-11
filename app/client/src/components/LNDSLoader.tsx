import LndsLogoImg from "./lnds-logo-only.png";
import { CSSProperties } from "react";

const loaderStyle: CSSProperties = {
  position: "fixed",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: "100px",
  height: "100px",
  animation: "rotate 2s linear infinite",
};

export const LNDSLoader = () => {
  return (
    <div style={loaderStyle}>
      <img src={LndsLogoImg} alt='Loading...' style={{ width: "100%", height: "100%" }} />
    </div>
  );
};

const css = document.createElement("style");
css.type = "text/css";
css.innerHTML = `@keyframes rotate { from { transform: translate(-50%, -50%) rotate(0deg); } to { transform: translate(-50%, -50%) rotate(360deg); } }`;
document.body.appendChild(css);
