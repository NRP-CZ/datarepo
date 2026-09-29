import React, { useEffect, useRef } from "react";
import * as L from "leaflet";
import "leaflet/dist/leaflet.css";
import "@geoman-io/leaflet-geoman-free";
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

export function GeolocationInteractiveMap() {
  const wrapperRef = useRef(null);
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [50, 14],
      zoom: 4,
    });

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    map.pm.addControls({
      position: "topright",
      drawCircle: false,
      drawCircleMarker: false,
      drawText: false,
      drawPolygon: true,
      drawMarker: true,
      drawPolyline: true,
      editMode: true,
      dragMode: true,
      cutPolygon: true,
      removalMode: true,
    });

    mapInstanceRef.current = map;

    const observer = new ResizeObserver(() => {
      map.invalidateSize({ animate: false });
    });
    observer.observe(wrapperRef.current);

    return () => {
      observer.disconnect();
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  return (
    <div
      ref={wrapperRef}
      style={{
        position: "relative",
        height: "100%",
        width: "100%",
        minHeight: 0,
      }}
    >
      <div
        ref={mapContainerRef}
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: "0.25em",
        }}
      />
    </div>
  );
}
