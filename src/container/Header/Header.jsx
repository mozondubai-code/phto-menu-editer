import React from "react";
import SubHeading from "../../components/SubHeading/SubHeading";

import "./Header.css";
import { images } from "../../constants";

const Header = () => {
  return (
    <div className="app__header " id="home">
      <div className="app__wrapper info">
        <SubHeading title="Chase the new flavour" />
        <h1 className="app__header-h1">The Key To Fine Dining</h1>
        <p className="p__opensans" style={{ margin: "2rem 0" }}>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Nam nostrum
          consequuntur sed. Provident commodi explicabo deleniti maiores magnam
          quisquam harum dolores voluptatum enim dolore! Reiciendis, repudiandae
          ab. Incidunt, eius ex.
        </p>
        <button className="custom__button">Explore Menu</button>
      </div>
      <div className="app__wrapper_img">
        <img
          src={images.welcome}
          alt="header img"
          style={{
            height: "450px",
            width: "400px",
            marginBottom: "100px",
            borderRadius: "10px",
          }}
        />
      </div>
    </div>
  );
};

export default Header;
