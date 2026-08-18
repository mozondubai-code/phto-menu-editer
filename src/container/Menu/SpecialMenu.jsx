import React from "react";

import { SubHeading, MenuItem } from "../../components";
import { data, images } from "../../constants";
import "./SpecialMenu.css";

const SpecialMenu = () => (
  <div className="specialMenu " id="menu">
    <div className="specialMenu-title">
      <SubHeading title="Menu that fits your palatte" />
      <h1 className="headtext">Today&apos;s Special</h1>
    </div>

    <div className="specialMenu-menu">
      <div className="wine">
        <p className="wine-heading">Wine & Beer</p>
        <div className="wine-list">
          {data.wines.map((wine, index) => (
            <MenuItem
              key={wine.title + index}
              title={wine.title}
              price={wine.price}
              tags={wine.tags}
            />
          ))}
        </div>
      </div>

      <div className="menu-img">
        <img src={images.menu} alt="menu img" />
      </div>

      <div className="cocktail">
        <p className="cocktail-heading">Cocktails</p>
        <div className="cocktail-list">
          {data.cocktails.map((cocktail, index) => (
            <MenuItem
              key={cocktail.title + index}
              title={cocktail.title}
              price={cocktail.price}
              tags={cocktail.tags}
            />
          ))}
        </div>
      </div>
    </div>

    <div className="menu-button">
      <button type="button" className="custom__button">
        View More
      </button>
    </div>
  </div>
);

export default SpecialMenu;
