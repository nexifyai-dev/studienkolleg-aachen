import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { Toaster } from 'sonner';
import { queryClient, QueryClientProvider } from './lib/query-client';
import './i18n';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ErrorBoundary } from './components/ErrorBoundary';
import ScrollToTop from './components/ScrollToTop';
import CookieBanner from './components/shared/CookieBanner';
import SupportChatWidget from './components/shared/SupportChatWidget';
import HomePage from './pages/public/HomePage';
import ApplyPage from './pages/public/ApplyPage';
import ContactPage from './pages/public/ContactPage';
import CoursesPage from './pages/public/CoursesPage';
import ServicesPage from './pages/public/ServicesPage';
import LegalPage from './pages/public/LegalPage';
import KnowledgeCenterPage from './pages/public/KnowledgeCenterPage';
import BookingPage from './pages/public/BookingPage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ApplicantLayout from './components/layout/ApplicantLayout';
import DashboardPage from './pages/portal/DashboardPage';
import JourneyPage from './pages/portal/JourneyPage';
import DocumentsPage from './pages/portal/DocumentsPage';
import MessagesPage from './pages/portal/MessagesPage';
import FinancialsPage from './pages/portal/FinancialsPage';
import SettingsPage from './pages/portal/SettingsPage';
import ConsentPage from './pages/portal/ConsentPage';
import ApplicantTasksPage from './pages/portal/ApplicantTasksPage';
import ApplicantMorePage from './pages/portal/ApplicantMorePage';
import StaffLayout from './components/layout/StaffLayout';
import StaffDashboard from './pages/staff/StaffDashboard';
import TeacherDashboard from './pages/staff/TeacherDashboard';
import KanbanPage from './pages/staff/KanbanPage';
import ApplicantDetailPage from './pages/staff/ApplicantDetailPage';
import StaffTasksPage from './pages/staff/StaffTasksPage';
import StaffMessagingPage from './pages/staff/StaffMessagingPage';
import StaffInvoicesPage from './pages/staff/StaffInvoicesPage';
import StaffCasesPage from './pages/staff/StaffCasesPage';
import StaffDocumentsReviewPage from './pages/staff/StaffDocumentsReviewPage';
import TeacherStudentsPage from './pages/staff/TeacherStudentsPage';
import TeacherStudentDetailPage from './pages/staff/TeacherStudentDetailPage';
import TeacherSupportPage from './pages/staff/TeacherSupportPage';
import TeacherMorePage from './pages/staff/TeacherMorePage';
import AdminLayout from './components/layout/AdminLayout';
import AdminDashboard from './pages/admin/AdminDashboard';
import UsersPage from './pages/admin/UsersPage';
import AuditPage from './pages/admin/AuditPage';
import AdminCasesPage from './pages/admin/AdminCasesPage';
import AdminPartnersPage from './pages/admin/AdminPartnersPage';
import AdminKnowledgePage from './pages/admin/AdminKnowledgePage';
import AdminJobsPage from './pages/admin/AdminJobsPage';
import AdminRulesPage from './pages/admin/AdminRulesPage';
import AdminReportsPage from './pages/admin/AdminReportsPage';
import AdminSettingsPage from './pages/admin/AdminSettingsPage';
import PartnerLayout from './components/layout/PartnerLayout';
import PartnerDashboardPage from './pages/partner/PartnerDashboardPage';
import PartnerReferralsPage from './pages/partner/PartnerReferralsPage';
import PartnerLinkPage from './pages/partner/PartnerLinkPage';
import PartnerSettingsPage from './pages/partner/PartnerSettingsPage';
import PartnerMessagesPage from './pages/partner/PartnerMessagesPage';
import PartnerTrackingPage from './pages/partner/PartnerTrackingPage';

// Lazy-loaded heavy pages
const LazyFallback = () => <div className="flex items-center justify-center min-h-[300px]"><div className="w2g-spinner" /></div>;
const ApplicantAppointmentsPage = lazy(() => import('./pages/portal/ApplicantAppointmentsPage'));
const StaffAppointmentsPage = lazy(() => import('./pages/staff/StaffAppointmentsPage'));
const StaffReportingPage = lazy(() => import('./pages/staff/StaffReportingPage'));
const OraclePage = lazy(() => import('./pages/staff/OraclePage'));

function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div></div>;
  if (!user) return <Navigate to="/auth/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/portal" replace />;
  return children;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (user) {
    const adminRoles = ['superadmin', 'admin'];
    const staffRoles = ['staff', 'accounting_staff', 'teacher'];
    if (adminRoles.includes(user.role)) return <Navigate to="/admin" replace />;
    if (staffRoles.includes(user.role)) return <Navigate to="/staff" replace />;
    if (['affiliate', 'agency_admin', 'agency_agent'].includes(user.role)) return <Navigate to="/partner" replace />;
    return <Navigate to="/portal" replace />;
  }
  return children;
}

// Dynamic staff index: Teacher sees TeacherDashboard, everyone else sees StaffDashboard
function StaffDashboardOrTeacher() {
  const { user } = useAuth();
  if (user?.role === 'teacher') return <TeacherDashboard />;
  return <StaffDashboard />;
}

export default function App() {
  return (
    <ErrorBoundary>
    <HelmetProvider>
    <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <BrowserRouter>
        <ScrollToTop />
        <CookieBanner />
        <SupportChatWidget />
        <Toaster position="top-right" richColors closeButton duration={3000} />
        <Routes>
          {/* Public */}
          <Route path="/" element={<HomePage />} />
          <Route path="/apply" element={<ApplyPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/knowledge" element={<KnowledgeCenterPage />} />
          <Route path="/legal" element={<LegalPage type="legal" />} />
          <Route path="/privacy" element={<LegalPage type="privacy" />} />
          <Route path="/agb" element={<LegalPage type="agb" />} />
          <Route path="/booking" element={<BookingPage />} />

          {/* Auth */}
          <Route path="/auth/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/auth/register" element={<RegisterPage />} />
          <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />

          {/* Applicant Portal */}
          <Route path="/portal" element={
            <ProtectedRoute allowedRoles={['applicant']}>
              <ApplicantLayout />
            </ProtectedRoute>
          }>
            <Route index element={<DashboardPage />} />
            <Route path="journey" element={<JourneyPage />} />
            <Route path="tasks" element={<ApplicantTasksPage />} />
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="messages" element={<MessagesPage />} />
            <Route path="financials" element={<FinancialsPage />} />
            <Route path="appointments" element={<Suspense fallback={<LazyFallback />}><ApplicantAppointmentsPage /></Suspense>} />
            <Route path="more" element={<ApplicantMorePage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="consents" element={<ConsentPage />} />
          </Route>

          {/* Staff */}
          <Route path="/staff" element={
            <ProtectedRoute allowedRoles={['superadmin','admin','staff','accounting_staff','teacher']}>
              <StaffLayout />
            </ProtectedRoute>
          }>
            <Route index element={<StaffDashboardOrTeacher />} />
            <Route path="kanban" element={<KanbanPage />} />
            <Route path="cases" element={<StaffCasesPage />} />
            <Route path="tasks" element={<StaffTasksPage />} />
            <Route path="messaging" element={<StaffMessagingPage />} />
            <Route path="documents" element={<StaffDocumentsReviewPage />} />
            <Route path="invoices" element={<StaffInvoicesPage />} />
            <Route path="reporting" element={<Suspense fallback={<LazyFallback />}><StaffReportingPage /></Suspense>} />
            <Route path="appointments" element={<Suspense fallback={<LazyFallback />}><StaffAppointmentsPage /></Suspense>} />
            <Route path="oracle" element={<Suspense fallback={<LazyFallback />}><OraclePage /></Suspense>} />
            <Route path="students" element={<TeacherStudentsPage />} />
            <Route path="students/:id" element={<TeacherStudentDetailPage />} />
            <Route path="teacher/messages" element={<TeacherSupportPage />} />
            <Route path="more" element={<TeacherMorePage />} />
            <Route path="applicants/:id" element={<ApplicantDetailPage />} />
            <Route path="applications/:id" element={<ApplicantDetailPage />} />
          </Route>

          {/* Admin */}
          <Route path="/admin" element={
            <ProtectedRoute allowedRoles={['superadmin','admin']}>
              <AdminLayout />
            </ProtectedRoute>
          }>
            <Route index element={<AdminDashboard />} />
            <Route path="cases" element={<AdminCasesPage />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="partners" element={<AdminPartnersPage />} />
            <Route path="knowledge" element={<AdminKnowledgePage />} />
            <Route path="jobs" element={<AdminJobsPage />} />
            <Route path="rules" element={<AdminRulesPage />} />
            <Route path="audit" element={<AuditPage />} />
            <Route path="reports" element={<AdminReportsPage />} />
            <Route path="settings" element={<AdminSettingsPage />} />
          </Route>

          {/* Partner / Affiliate */}
          <Route path="/partner" element={
            <ProtectedRoute allowedRoles={['affiliate','agency_admin','agency_agent','superadmin','admin']}>
              <PartnerLayout />
            </ProtectedRoute>
          }>
            <Route index element={<PartnerDashboardPage />} />
            <Route path="referrals" element={<PartnerReferralsPage />} />
            <Route path="tracking" element={<PartnerTrackingPage />} />
            <Route path="link" element={<PartnerLinkPage />} />
            <Route path="messages" element={<PartnerMessagesPage />} />
            <Route path="settings" element={<PartnerSettingsPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
    </QueryClientProvider>
    </HelmetProvider>
    </ErrorBoundary>
  );
}
