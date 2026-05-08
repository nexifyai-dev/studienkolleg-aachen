/**
 * CSRF Double-Submit Cookie – Hilfsfunktionen.
 *
 * Liest den csrf_token-Cookie und liefert den Wert,
 * damit Axios-Interceptors ihn als x-csrf-token Header setzen koennen.
 */

const CSRF_COOKIE_NAME = 'csrf_token';
const CSRF_HEADER_NAME = 'x-csrf-token';
const UNSAFE_METHODS = ['post', 'put', 'delete', 'patch'];

/**
 * Liest einen Cookie-Wert anhand des Namens.
 */
function getCookie(name) {
  const match = document.cookie.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : null;
}

/**
 * Gibt den aktuellen CSRF-Token aus dem Cookie zurueck.
 */
export function getCsrfToken() {
  return getCookie(CSRF_COOKIE_NAME);
}

/**
 * Axios Request-Interceptor: Haengt bei unsafe Methods
 * den CSRF-Token als Header an.
 */
export function csrfRequestInterceptor(config) {
  const method = (config.method || 'get').toLowerCase();
  if (UNSAFE_METHODS.includes(method)) {
    const token = getCsrfToken();
    if (token) {
      config.headers = config.headers || {};
      config.headers[CSRF_HEADER_NAME] = token;
    }
  }
  return config;
}
