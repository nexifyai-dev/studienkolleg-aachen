/**
 * Resolves the API base URL with cross-domain safety.
 *
 * Why this exists:
 *   `process.env.REACT_APP_BACKEND_URL` is baked into the React bundle at
 *   build time. When the same bundle is served on a custom domain (e.g.
 *   studienkolleg.nexifyai.de) but the env var still points at the original
 *   deployment URL (e.g. block11-layout.emergent.host), every API request
 *   becomes cross-site. Browsers — especially iOS Safari (ITP) and modern
 *   Chrome — block third-party cookies in that scenario, which causes
 *   intermittent / mobile-only login failures.
 *
 * Behaviour:
 *   - If REACT_APP_BACKEND_URL points at the SAME host the user is currently
 *     on, use it as-is (preserves explicit configuration).
 *   - If it points at a DIFFERENT host, fall back to an empty base URL so
 *     all requests stay first-party (cookies set on the user's domain).
 *   - SSR / no-window context: return the configured value verbatim.
 */
const _configured = process.env.REACT_APP_BACKEND_URL || '';

function _resolveApiBase() {
  if (typeof window === 'undefined' || !_configured) return _configured;
  try {
    const configuredHost = new URL(_configured).host;
    if (configuredHost && configuredHost !== window.location.host) {
      return '';
    }
  } catch (e) {
    // malformed env value -> fall through to configured (may still work)
  }
  return _configured;
}

export const API = _resolveApiBase();
export default API;
