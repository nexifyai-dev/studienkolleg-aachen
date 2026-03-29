import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './i18n';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ScrollToTop from './components/ScrollToTop';
import CookieBanner from './components/shared/CookieBanner';

// Public pages
import HomePage from './pages/public/HomePage';
import ApplyPage from './pages/public/ApplyPage';
import ContactPage from './pages/public/ContactPage';
import CoursesPage from './pages/public/CoursesPage';
import ServicesPage from './pages/public/ServicesPage';
import LegalPage from './pages/public/LegalPage';

// Auth pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';

// Portal pages (applicant)
import ApplicantLayout from './components/layout/ApplicantLayout';
import DashboardPage from './pages/portal/DashboardPage';
import JourneyPage from './pages/portal/JourneyPage';
import DocumentsPage from './pages/portal/DocumentsPage';
import MessagesPage from './pages/portal/MessagesPage';
import FinancialsPage from './pages/portal/FinancialsPage';
import SettingsPage from './pages/portal/SettingsPage';
import ConsentPage from './pages/portal/ConsentPage';

// Staff pages
import StaffLayout from './components/layout/StaffLayout';
import StaffDashboard from './pages/staff/StaffDashboard';
import TeacherDashboard from './pages/staff/TeacherDashboard';
import KanbanPage from './pages/staff/KanbanPage';
import ApplicantDetailPage from './pages/staff/ApplicantDetailPage';

// Admin pages
import AdminLayout from './components/layout/AdminLayout';
import AdminDashboard from './pages/admin/AdminDashboard';
import UsersPage from './pages/admin/UsersPage';
import AuditPage from './pages/admin/AuditPage';

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
    const staffRoles = ['superadmin', 'admin', 'staff', 'accounting_staff', 'teacher'];
    if (staffRoles.includes(user.role)) return <Navigate to="/staff" replace />;
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
    <AuthProvider>
      <BrowserRouter>
        <ScrollToTop />
        <CookieBanner />
        <Routes>
          {/* Public */}
          <Route path="/" element={<HomePage />} />
          <Route path="/apply" element={<ApplyPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/legal" element={<LegalPage type="legal" />} />
          <Route path="/privacy" element={<LegalPage type="privacy" />} />
          <Route path="/agb" element={<LegalPage type="agb" />} />

          {/* Auth */}
          <Route path="/auth/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/auth/register" element={<RegisterPage />} />
          <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />

          {/* Applicant Portal */}
          <Route path="/portal" element={
            <ProtectedRoute allowedRoles={['applicant', 'affiliate']}>
              <ApplicantLayout />
            </ProtectedRoute>
          }>
            <Route index element={<DashboardPage />} />
            <Route path="journey" element={<JourneyPage />} />
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="messages" element={<MessagesPage />} />
            <Route path="financials" element={<FinancialsPage />} />
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
            <Route path="users" element={<UsersPage />} />
            <Route path="audit" element={<AuditPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
