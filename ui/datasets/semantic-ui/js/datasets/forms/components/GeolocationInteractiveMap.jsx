import React, { useEffect, useRef } from "react";
import PropTypes from "prop-types";
import * as L from "leaflet";
import "leaflet/dist/leaflet.css";
import "@geoman-io/leaflet-geoman-free";
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

// Strips away Leaflet's path-guessing function.
delete L.Icon.Default.prototype._getIconUrl;
// Injects the safe, Webpack-approved URLs directly into Leaflet's global default icon configuration.
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

/**
 * Splits any GeoJSON geometry into simple Point / LineString / Polygon parts.
 * (Multi* and GeometryCollection are flattened, recursively.)
 */
function splitsToSimpleGeometries(geometry) {
  if (!geometry) return [];

  switch (geometry.type) {
    case "GeometryCollection":
      return (geometry.geometries ?? []).flatMap(splitsToSimpleGeometries);
    case "MultiPoint":
    case "MultiLineString":
    case "MultiPolygon": {
      const type = geometry.type.replace("Multi", "");
      return (geometry.coordinates ?? []).map((coordinates) => ({
        type,
        coordinates,
      }));
    }
    case "Point":
    case "LineString":
    case "Polygon":
      return [geometry];
    default:
      return [];
  }
}

/**
 * Merges any GeoJSON geometries into ONE geometry:
 *  - nothing                 -> null
 *  - one shape               -> Point / LineString / Polygon
 *  - several of the same     -> MultiPoint / MultiLineString / MultiPolygon
 *  - several different types -> GeometryCollection of the above
 */
function mergeGeometries(geometries) {
  const simple = geometries.flatMap(splitsToSimpleGeometries);
  if (!simple.length) return null;

  const geometriesByType = {};
  for (const { type, coordinates } of simple) {
    (geometriesByType[type] ||= []).push(coordinates);
  }

  const parts = Object.entries(geometriesByType).map(([type, coords]) =>
    coords.length === 1
      ? { type, coordinates: coords[0] }
      : { type: `Multi${type}`, coordinates: coords },
  );

  return parts.length === 1
    ? parts[0]
    : { type: "GeometryCollection", geometries: parts };
}

export function GeolocationInteractiveMap({
  initialMapSettings,
  geometry,
  onGeometryChange,
}) {
  // Standart references for <div> wrapper (used for ResizeObserver), map container and instance.
  const wrapperRef = useRef(null);
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);

  // Holds the function capable of updating map geometries when the parent's geometry prop changes.
  const syncRef = useRef(null);
  // Last emitted geometry from the interactive map.
  const lastEmittedRef = useRef("null");

  // Tracks the freshest version of onGeometryChange without triggering a re-render or re-running the map initialization
  const onChangeRef = useRef(onGeometryChange);
  useEffect(() => {
    onChangeRef.current = onGeometryChange;
  }, [onGeometryChange]);

  // Initialization of map.
  useEffect(() => {
    if (mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, initialMapSettings);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    map.pm.addControls({
      position: "topright",
      drawMarker: true,
      drawPolyline: true,
      drawPolygon: true,
      drawRectangle: true,
      drawCircle: false,
      drawCircleMarker: false,
      drawText: false,
      editMode: true,
      dragMode: true,
      cutPolygon: true,
      removalMode: true,
    });

    const group = L.featureGroup().addTo(map);
    lastEmittedRef.current = "null";

    /**
     * Grabs geometries from all layers and merge them.
     * Follows by storing merged geometry in `lastEmittedRef` reference and firing up the `onChange` listener.
     */
    const emit = () => {
      const geoms = [];
      group.eachLayer((layer) => {
        const geom = layer.toGeoJSON().geometry;
        if (geom) geoms.push(geom);
      });
      const merged = mergeGeometries(geoms);
      lastEmittedRef.current = JSON.stringify(merged);
      onChangeRef.current?.(merged);
    };

    /**
     * Adds layer into the feature group and adds listeners on layer's edit and drag events.
     * @param layer layer
     */
    const track = (layer) => {
      group.addLayer(layer);
      layer.on("pm:edit", emit);
      layer.on("pm:dragend", emit);
      layer.on("pm:markerdragend", emit);
    };

    /**
     * Accepts a GeoJSON geometry passed in from the parent component
     * and physically translates it into interactive shapes on the Leaflet map
     * @param geometries geometries
     * @returns true if drawing was successfull, otherwise false
     */
    syncRef.current = (geometries) => {
      let layers;
      try {
        layers = splitsToSimpleGeometries(geometries)
          .map((g) => L.geoJSON(g).getLayers()[0])
          .filter(Boolean);
      } catch {
        return false;
      }

      group.clearLayers();
      layers.forEach(track);

      if (layers.length) {
        const bounds = group.getBounds();
        if (bounds.isValid()) {
          map.fitBounds(bounds, { maxZoom: 14, padding: [20, 20] });
        }
      }
      return true;
    };

    map.on("pm:create", ({ layer }) => {
      track(layer);
      emit();
    });

    map.on("pm:remove", ({ layer }) => {
      group.removeLayer(layer);
      emit();
    });

    map.on("pm:cut", ({ layer, originalLayer }) => {
      if (originalLayer) group.removeLayer(originalLayer);
      if (layer && !group.hasLayer(layer)) track(layer);
      emit();
    });

    mapInstanceRef.current = map;

    const observer = new ResizeObserver(() => {
      map.invalidateSize({ animate: false });
    });
    observer.observe(wrapperRef.current);

    return () => {
      observer.disconnect();
      syncRef.current = null;
      map.remove();
      mapInstanceRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Watches the geometry passed in from the parent and decides whether the Leaflet map needs to be redrawn.
  const geometryKey = JSON.stringify(geometry ?? null);
  useEffect(() => {
    if (geometryKey === lastEmittedRef.current) return;
    if (!syncRef.current) return;
    // Draw geometries on the map.
    if (syncRef.current(JSON.parse(geometryKey))) {
      lastEmittedRef.current = geometryKey;
    }
  }, [geometryKey]);

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
        style={{ position: "absolute", inset: 0, borderRadius: "0.25em" }}
      />
    </div>
  );
}

GeolocationInteractiveMap.propTypes = {
  initialMapSettings: PropTypes.shape({
    center: PropTypes.array,
    zoom: PropTypes.number,
  }),
  geometry: PropTypes.object,
  onGeometryChange: PropTypes.func,
};
