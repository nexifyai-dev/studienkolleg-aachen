import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { csrfRequestInterceptor } from './csrf';
import { API } from './apiBase';

const api = axios.create({ baseURL: `${API}/api`, withCredentials: true });

// CSRF-Token bei allen unsafe Requests automatisch mitsenden
api.interceptors.request.use(csrfRequestInterceptor);

/* ═══════════════════════════════════════════════════════════════════════
   W2G API HOOKS – Zentrale Server-State-Verwaltung
   Alle API-Aufrufe ueber TanStack Query mit automatischem Caching,
   Background Refresh und optimistischen Updates.
   ═══════════════════════════════════════════════════════════════════════ */

/* ─── AUTH ─────────────────────────────────────────────────────────────── */
export function useCurrentUser() {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => api.get('/auth/me').then(r => r.data),
    retry: false,
    staleTime: 60 * 1000,
  });
}

/* ─── APPLICATIONS ────────────────────────────────────────────────────── */
export function useApplications(params = {}) {
  return useQuery({
    queryKey: ['applications', params],
    queryFn: () => api.get('/applications', { params }).then(r => r.data),
  });
}

export function useApplication(id) {
  return useQuery({
    queryKey: ['applications', id],
    queryFn: () => api.get(`/applications/${id}`).then(r => r.data),
    enabled: !!id,
  });
}

export function useUpdateApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(`/applications/${id}`, data).then(r => r.data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: ['applications', id] });
      qc.invalidateQueries({ queryKey: ['applications'] });
    },
  });
}

/* ─── INVOICES ────────────────────────────────────────────────────────── */
export function useInvoices(params = {}) {
  return useQuery({
    queryKey: ['invoices', params],
    queryFn: () => api.get('/invoices', { params }).then(r => r.data),
  });
}

export function useInvoice(id) {
  return useQuery({
    queryKey: ['invoices', id],
    queryFn: () => api.get(`/invoices/${id}`).then(r => r.data),
    enabled: !!id,
  });
}

export function useCreateInvoice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post('/invoices', data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['invoices'] }),
  });
}

/* ─── DOCUMENTS ───────────────────────────────────────────────────────── */
export function useDocuments(appId) {
  return useQuery({
    queryKey: ['documents', appId],
    queryFn: () => api.get(`/documents/${appId}`).then(r => r.data),
    enabled: !!appId,
  });
}

export function useMyDocuments() {
  return useQuery({
    queryKey: ['documents', 'my'],
    queryFn: () => api.get('/documents/my').then(r => r.data),
  });
}

/* ─── TASKS ───────────────────────────────────────────────────────────── */
export function useTasks(params = {}) {
  return useQuery({
    queryKey: ['tasks', params],
    queryFn: () => api.get('/tasks', { params }).then(r => r.data),
  });
}

export function useCreateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post('/tasks', data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks'] }),
  });
}

export function useUpdateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(`/tasks/${id}`, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks'] }),
  });
}

/* ─── MESSAGING ───────────────────────────────────────────────────────── */
export function useConversations() {
  return useQuery({
    queryKey: ['conversations'],
    queryFn: () => api.get('/conversations').then(r => r.data),
  });
}

export function useConversation(id) {
  return useQuery({
    queryKey: ['conversations', id],
    queryFn: () => api.get(`/conversations/${id}`).then(r => r.data),
    enabled: !!id,
    refetchInterval: 10 * 1000,
  });
}

export function useSendMessage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ convId, data }) => api.post(`/conversations/${convId}/messages`, data).then(r => r.data),
    onSuccess: (_, { convId }) => qc.invalidateQueries({ queryKey: ['conversations', convId] }),
  });
}

/* ─── NOTIFICATIONS ───────────────────────────────────────────────────── */
export function useNotifications() {
  return useQuery({
    queryKey: ['notifications'],
    queryFn: () => api.get('/notifications').then(r => r.data),
    refetchInterval: 30 * 1000,
  });
}

/* ─── DASHBOARD STATS ─────────────────────────────────────────────────── */
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => api.get('/dashboard/stats').then(r => r.data),
    staleTime: 60 * 1000,
  });
}

/* ─── ANABIN ──────────────────────────────────────────────────────────── */
export function useAnabinEntries(params = {}) {
  return useQuery({
    queryKey: ['anabin', params],
    queryFn: () => api.get('/anabin/entries', { params }).then(r => r.data),
  });
}

/* ─── USERS ───────────────────────────────────────────────────────────── */
export function useUsers(params = {}) {
  return useQuery({
    queryKey: ['users', params],
    queryFn: () => api.get('/users', { params }).then(r => r.data),
  });
}

/* ─── APPOINTMENTS ────────────────────────────────────────────────────── */
export function useAppointments() {
  return useQuery({
    queryKey: ['appointments'],
    queryFn: () => api.get('/appointments').then(r => r.data),
  });
}

export function usePublicSlots() {
  return useQuery({
    queryKey: ['appointments', 'public-slots'],
    queryFn: () => api.get('/appointments/public-slots').then(r => r.data),
    staleTime: 5 * 60 * 1000,
  });
}

/* ─── PARTNER ─────────────────────────────────────────────────────────── */
export function usePartnerDashboard() {
  return useQuery({
    queryKey: ['partner', 'dashboard'],
    queryFn: () => api.get('/partner/dashboard').then(r => r.data),
  });
}

/* ─── GENERIC HELPER ──────────────────────────────────────────────────── */
export { api };

/* ─── BATCH SCREENING ─────────────────────────────────────────────────── */
export function useBatchScreening() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (applicationIds) =>
      api.post('/ai-screening/batch', { application_ids: applicationIds }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries(['applications']),
  });
}

export function useBatchStatus(batchId) {
  return useQuery({
    queryKey: ['batch-screening', batchId],
    queryFn: () => api.get(`/ai-screening/batch/${batchId}/status`).then(r => r.data),
    enabled: !!batchId,
    refetchInterval: (data) => data?.progress?.is_done ? false : 2000,
  });
}

/* ─── PAYMENTS ────────────────────────────────────────────────────────── */
export function useCreateCheckout() {
  return useMutation({
    mutationFn: ({ invoiceNumber, originUrl }) =>
      api.post('/payments/checkout', { invoice_number: invoiceNumber, origin_url: originUrl }).then(r => r.data),
  });
}

export function usePaymentStatus(sessionId) {
  return useQuery({
    queryKey: ['payment', sessionId],
    queryFn: () => api.get(`/payments/status/${sessionId}`).then(r => r.data),
    enabled: !!sessionId,
  });
}

export function usePaymentTransactions() {
  return useQuery({
    queryKey: ['payments', 'transactions'],
    queryFn: () => api.get('/payments/transactions').then(r => r.data),
  });
}