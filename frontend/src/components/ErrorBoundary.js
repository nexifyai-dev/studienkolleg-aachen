import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info?.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          data-testid="error-boundary-fallback"
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--color-surface, #F0F4F8)',
            fontFamily: 'var(--font-body, Inter, sans-serif)',
          }}
        >
          <div style={{ textAlign: 'center', maxWidth: 440, padding: '0 24px' }}>
            <div style={{
              width: 56, height: 56, borderRadius: 'var(--radius-md, 4px)',
              background: 'var(--color-primary, #113655)', display: 'flex',
              alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px',
            }}>
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <h2 style={{
              color: 'var(--color-text-primary, #0a2036)',
              fontSize: 18, fontWeight: 700, margin: '0 0 8px',
              letterSpacing: '-0.3px',
            }}>
              Ein Fehler ist aufgetreten
            </h2>
            <p style={{
              color: 'var(--color-text-secondary, #4B5563)',
              fontSize: 14, lineHeight: 1.6, margin: '0 0 24px',
            }}>
              Die Seite konnte nicht geladen werden. Bitte lade die Seite neu oder kontaktiere den Support.
            </p>
            <button
              data-testid="error-boundary-reload"
              onClick={() => window.location.reload()}
              style={{
                background: 'var(--color-primary, #113655)',
                color: 'white', border: 'none', padding: '10px 24px',
                borderRadius: 'var(--radius-sm, 2px)',
                fontSize: 14, fontWeight: 600, cursor: 'pointer',
                letterSpacing: '-0.2px',
              }}
            >
              Seite neu laden
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
