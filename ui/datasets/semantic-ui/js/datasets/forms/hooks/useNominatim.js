// SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
// SPDX-License-Identifier: MIT

import { useState, useCallback, useRef } from "react";
import { i18next } from "@translations/i18next";
import axios from "axios";

export function useNominatim() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // References to hold the current abort controllers.
  const searchAbortControllerRef = useRef(null);
  const reverseAbortControllerRef = useRef(null);

  const searchLocation = useCallback(async (query) => {
    if (searchAbortControllerRef.current) {
      searchAbortControllerRef.current.abort();
    }
    searchAbortControllerRef.current = new AbortController();

    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        "https://nominatim.openstreetmap.org/search",
        {
          params: { q: query, format: "jsonv2", addressdetails: 1 },
          signal: searchAbortControllerRef.current.signal,
        }
      );
      return response.data;
    } catch (e) {
      if (axios.isCancel(e)) {
        console.log("Previous search request was canceled.");
        return [];
      }
      setError(i18next.t("Location search failed!"));
      console.error(`Location search failed: <${e}>!`);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reverseLocation = useCallback(async (lat, lon) => {
    if (reverseAbortControllerRef.current) {
      reverseAbortControllerRef.current.abort();
    }
    reverseAbortControllerRef.current = new AbortController();

    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        "https://nominatim.openstreetmap.org/reverse",
        {
          params: { lat: lat, lon: lon, format: "jsonv2" },
          signal: reverseAbortControllerRef.current.signal,
        }
      );
      return response.data;
    } catch (e) {
      if (axios.isCancel(e)) {
        console.log("Previous reverse geocoding canceled");
        return null;
      }
      setError(i18next.t("Reverse geocoding failed!"));
      console.error(`Reverse geocoding failed: <${e}>!`);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { searchLocation, reverseLocation, isLoading, error };
}