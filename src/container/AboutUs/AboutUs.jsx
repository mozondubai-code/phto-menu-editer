import React from "react";
import { images } from "../../constants";

import "./AboutUs.css";

const AboutUs = () => {
  return (
    <div className="aboutus-outer">
      <div className="aboutus">
        <div className="aboutus-left aboutus-content">
          <h1 classname="headtext">About Us</h1>
          <img src={images.spoon} alt="about_spoon" className="spoon__img" />
          <p className="p__opensaans">
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Quam veniam
            ullam quibusdam deleniti molestias odit explicabo error saepe,
            voluptatum, aspernatur dicta nisi enim animi accusantium cumque
            porro eum labore magni!
          </p>
          <button type="button" className="custom__button">
            Know More
          </button>
        </div>
        <div className="knife aboutus-content">
          <img
            src={images.knife}
            alt="knife"
            style={{ height: "420px", width: "50px" }}
          />
        </div>
        <div className="aboutus-right aboutus-content">
          <h1 classname="headtext">Our History</h1>
          <img src={images.spoon} alt="about_spoon" className=" spoon__img" />
          <p className="p__opensaans">
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Quam veniam
            ullam quibusdam deleniti molestias odit explicabo error saepe,
            voluptatum, aspernatur dicta nisi enim animi accusantium cumque
            porro eum labore magni!
          </p>
          <button type="button" className="custom__button">
            Know More
          </button>
        </div>
      </div>
    </div>
  );
};

export default AboutUs;
