/**
 * Service-Worker Registrierung – nur in Produktion,
 * kein Registrieren in localhost/dev/CRA-Preview.
 */
export function registerServiceWorker() {
  if (typeof window === 'undefined') return;
  if (!('serviceWorker' in navigator)) return;
  // Nur wenn HTTPS (Kubernetes-Preview/Prod haben HTTPS via Ingress)
  if (window.location.protocol !== 'https:') return;

  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then((registration) => {
        // Auf neue Version prüfen alle 60min
        setInterval(() => registration.update().catch(() => {}), 60 * 60 * 1000);
      })
      .catch(() => {
        // Kein Log – SW-Registrierung ist optional
      });
  });
}
