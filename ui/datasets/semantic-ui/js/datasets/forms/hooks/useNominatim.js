import { useState, useCallback } from "react";
import { i18next } from "@translations/ccmm_invenio";
import axios from "axios";

export function useNominatim() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const searchLocation = useCallback(async (query) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        "https://nominatim.openstreetmap.org/search",
        {
          params: { q: query, format: "jsonv2", addressdetails: 1 },
        }
      );
      return response.data;
    } catch (e) {
      setError(i18next.t("Location search failed!"));
      console.error(`Location search failed: <${e}>!`)
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reverseLocation = useCallback(async (lat, lon) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        "https://nominatim.openstreetmap.org/reverse",
        {
          params: { lat: lat, lon: lon, format: "jsonv2" },
        }
      );
      return response.data;
    } catch (e) {
      setError(i18next.t("Reverse geocoding failed!"));
      console.error(`Reverse geocoding failed: <${e}>!`)
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { searchLocation, reverseLocation, isLoading, error };
}