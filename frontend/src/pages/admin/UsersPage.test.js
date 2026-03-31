import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UsersPage from './UsersPage';
import apiClient from '../../lib/apiClient';

jest.mock('../../lib/apiClient');

describe('UsersPage error handling', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('shows normalized API error when invite request fails', async () => {
    apiClient.get.mockResolvedValueOnce({ data: [] });
    apiClient.post.mockRejectedValueOnce({
      response: { status: 422, data: { detail: [{ msg: 'Ungültige E-Mail' }] } },
    });

    render(<UsersPage />);

    await screen.findByTestId('invite-user-btn');
    await userEvent.click(screen.getByTestId('invite-user-btn'));

    await userEvent.type(screen.getByTestId('invite-email-input'), 'invalid@example.com');
    await userEvent.type(screen.getByTestId('invite-name-input'), 'Max Mustermann');
    await userEvent.click(screen.getByTestId('invite-submit-btn'));

    await waitFor(() => {
      expect(screen.getByText('Ungültige E-Mail')).toBeInTheDocument();
    });
  });
});
