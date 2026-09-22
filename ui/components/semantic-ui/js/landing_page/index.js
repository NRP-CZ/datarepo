import React from "react";
import ReactDOM from "react-dom";
import Locations from "./components/Locations";

const recordLocationsContainer = document.getElementById("record-locations");

if (recordLocationsContainer) {
  ReactDOM.render(
    <Locations
      locations={recordLocationsContainer.getAttribute("data-locations")}
    />,
    recordLocationsContainer,
  );
}
