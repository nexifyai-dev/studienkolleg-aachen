import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * ScrollToTop – scrollt bei jedem Routenwechsel automatisch zum Seitenanfang.
 * Eingebunden in App.js direkt unterhalb von <BrowserRouter>.
 */
export default function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, [pathname]);
  return null;
}
