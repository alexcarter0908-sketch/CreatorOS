export interface UserLocation {
  latitude: number;
  longitude: number;
}

const LOCATION_CACHE_KEY = "creatoros_last_location";
const LOCATION_CACHE_TTL_MS = 15 * 60 * 1000; // 15 minutes

/**
 * Requests the user's current location via the browser Geolocation API.
 * Returns null (never throws) if permission is denied, unsupported, or
 * the request times out - callers should treat "no location" as a
 * completely normal, expected case and continue without it.
 *
 * Caches the last successful location briefly (sessionStorage) to
 * avoid re-prompting/re-querying on every single message.
 */
export async function getUserLocation(): Promise<UserLocation | null> {
  if (typeof window === "undefined" || !("geolocation" in navigator)) {
    return null;
  }

  const cached = readCachedLocation();
  if (cached) return cached;

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location: UserLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        };
        writeCachedLocation(location);
        resolve(location);
      },
      () => {
        resolve(null);
      },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 }
    );
  });
}

function readCachedLocation(): UserLocation | null {
  try {
    const raw = sessionStorage.getItem(LOCATION_CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as UserLocation & { cachedAt: number };
    if (Date.now() - parsed.cachedAt > LOCATION_CACHE_TTL_MS) return null;
    return { latitude: parsed.latitude, longitude: parsed.longitude };
  } catch {
    return null;
  }
}

function writeCachedLocation(location: UserLocation) {
  try {
    sessionStorage.setItem(
      LOCATION_CACHE_KEY,
      JSON.stringify({ ...location, cachedAt: Date.now() })
    );
  } catch {
    // sessionStorage can throw in private/incognito contexts - ignore
  }
}
