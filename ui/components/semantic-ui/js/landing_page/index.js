import React from "react";
import ReactDOM from "react-dom";
import Locations from "./components/Locations";

const recordLocationsContainer = document.getElementById("record-locations");

if (recordLocationsContainer) {
  const locations = JSON.parse(
    recordLocationsContainer.getAttribute("data-locations"),
  );

  ReactDOM.render(
    <Locations locations={locations} />,
    recordLocationsContainer,
  );
}
