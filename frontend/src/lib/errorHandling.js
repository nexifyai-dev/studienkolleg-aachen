import { toast } from 'sonner';

function normalizeDetail(detail) {
  if (!detail) return '';
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item;
        if (item?.msg) return item.msg;
        if (item?.message) return item.message;
        return '';
      })
      .filter(Boolean)
      .join(' · ');
  }
  if (typeof detail === 'object') {
    if (detail.message) return String(detail.message);
    if (detail.error) return String(detail.error);
    try {
      return JSON.stringify(detail);
    } catch {
      return String(detail);
    }
  }
  return String(detail);
}

export function normalizeApiError(error, fallback = 'Ein unerwarteter Fehler ist aufgetreten.') {
  const detail = error?.response?.data?.detail ?? error?.response?.data ?? error?.message;
  const normalized = normalizeDetail(detail);
  return normalized || fallback;
}

export function handleApiError(error, {
  context,
  toastMessage,
  fallbackMessage,
  suppressToast = false,
  suppressLog = false,
  logLevel = 'debug',
  extra,
} = {}) {
  const message = normalizeApiError(error, fallbackMessage);

  if (!suppressLog) {
    const payload = {
      context,
      message,
      status: error?.response?.status,
      data: error?.response?.data,
      extra,
    };
    if (logLevel === 'error') {
      console.error('[api-error]', payload);
    } else {
      console.debug('[api-error]', payload);
    }
  }

  if (!suppressToast && toastMessage) {
    const text = message && message !== toastMessage
      ? `${toastMessage}: ${message}`
      : toastMessage;
    toast.error(text);
  }

  return message;
}
