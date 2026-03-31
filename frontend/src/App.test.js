import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ProtectedRoute, PublicRoute, resolveHomeByRole } from './App';
import { useAuth } from './contexts/AuthContext';

jest.mock('./contexts/AuthContext', () => ({
  useAuth: jest.fn(),
  AuthProvider: ({ children }) => <>{children}</>,
}));

const mockedUseAuth = useAuth;

function renderWithRoutes(ui, initialEntry) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>{ui}</Routes>
    </MemoryRouter>
  );
}

describe('role-based route guards', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('unzulässiger Zugriff auf /admin als staff führt zu /staff', () => {
    mockedUseAuth.mockReturnValue({
      user: { role: 'staff' },
      loading: false,
    });

    renderWithRoutes(
      <>
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={['superadmin', 'admin']}>
              <div>Admin Area</div>
            </ProtectedRoute>
          }
        />
        <Route path="/staff" element={<div>Staff Home</div>} />
        <Route path="/portal" element={<div>Applicant Portal</div>} />
      </>,
      '/admin'
    );

    expect(screen.getByText('Staff Home')).toBeInTheDocument();
    expect(screen.queryByText('Applicant Portal')).not.toBeInTheDocument();
  });

  test('unzulässiger Zugriff auf /staff als applicant führt zu /portal', () => {
    mockedUseAuth.mockReturnValue({
      user: { role: 'applicant' },
      loading: false,
    });

    renderWithRoutes(
      <>
        <Route
          path="/staff"
          element={
            <ProtectedRoute allowedRoles={['superadmin', 'admin', 'staff', 'accounting_staff', 'teacher']}>
              <div>Staff Area</div>
            </ProtectedRoute>
          }
        />
        <Route path="/portal" element={<div>Applicant Portal</div>} />
      </>,
      '/staff'
    );

    expect(screen.getByText('Applicant Portal')).toBeInTheDocument();
  });

  test('PublicRoute nutzt dieselbe Zielauflösung für affiliate', () => {
    mockedUseAuth.mockReturnValue({
      user: { role: 'affiliate' },
      loading: false,
    });

    renderWithRoutes(
      <>
        <Route
          path="/auth/login"
          element={
            <PublicRoute>
              <div>Login</div>
            </PublicRoute>
          }
        />
        <Route path="/partner" element={<div>Partner Home</div>} />
      </>,
      '/auth/login'
    );

    expect(screen.getByText('Partner Home')).toBeInTheDocument();
  });
});

describe('resolveHomeByRole', () => {
  test('löst Startseiten konsistent je Rolle auf', () => {
    expect(resolveHomeByRole('admin')).toBe('/admin');
    expect(resolveHomeByRole('staff')).toBe('/staff');
    expect(resolveHomeByRole('affiliate')).toBe('/partner');
    expect(resolveHomeByRole('applicant')).toBe('/portal');
  });
});
