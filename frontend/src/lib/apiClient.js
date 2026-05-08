/**
 * Configured axios instance with:
 * - Automatic JWT access token refresh on 401
 * - Single retry per request (no retry loop)
 * - Redirect to /auth/login on complete auth failure
 *
 * Security notes:
 * - Credentials (cookies) always sent with `withCredentials: true`
 * - On 401: first tries POST /api/auth/refresh (uses refresh cookie)
 * - On refresh failure: clears local user state, redirects to login
 * - No tokens stored in localStorage (httpOnly cookies only)
 */
import axios from 'axios';
import { csrfRequestInterceptor, getCsrfToken } from './csrf';
import { API } from './apiBase';

const CSRF_HEADER = 'x-csrf-token';

const apiClient = axios.create({
  baseURL: API,
  withCredentials: true,
});

// CSRF-Token bei allen unsafe Requests automatisch mitsenden
apiClient.interceptors.request.use(csrfRequestInterceptor);

let isRefreshing = false;
let failedQueue = [];

function processQueue(error) {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });
  failedQueue = [];
}

apiClient.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config;

    // Only attempt refresh on 401 from non-auth endpoints
    if (
      err.response?.status === 401 &&
      !original._retry &&
      !original.url?.includes('/api/auth/')
    ) {
      if (isRefreshing) {
        // Queue requests during refresh
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => apiClient(original)).catch(e => Promise.reject(e));
      }

      original._retry = true;
      isRefreshing = true;

      try {
        await axios.post(`${API}/api/auth/refresh`, {}, {
          withCredentials: true,
          headers: { [CSRF_HEADER]: getCsrfToken() || '' },
        });
        processQueue(null);
        return apiClient(original);
      } catch (refreshError) {
        processQueue(refreshError);
        // Refresh failed – clear state and redirect
        try {
          await axios.post(`${API}/api/auth/logout`, {}, {
            withCredentials: true,
            headers: { [CSRF_HEADER]: getCsrfToken() || '' },
          });
        } catch {}
        window.location.href = '/auth/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(err);
  }
);

export default apiClient;
