import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import MessagesPage from './MessagesPage';
import apiClient from '../../lib/apiClient';
import { toast } from 'sonner';

jest.mock('../../lib/apiClient');
jest.mock('sonner', () => ({
  toast: { error: jest.fn(), success: jest.fn() },
}));
jest.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key) => key }),
}));
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ user: { id: 'user-1' } }),
}));

describe('MessagesPage error handling', () => {
  beforeAll(() => {
    Object.defineProperty(window.HTMLElement.prototype, 'scrollIntoView', {
      configurable: true,
      value: jest.fn(),
    });
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('shows contextual toast and resets sending state when message send fails', async () => {
    apiClient.get
      .mockResolvedValueOnce({ data: { id: 'conv-1', participant_names: {} } })
      .mockResolvedValueOnce({ data: [{ id: 'conv-1', participant_names: { 'staff-1': 'Team' } }] })
      .mockResolvedValueOnce({ data: [] });

    apiClient.post.mockRejectedValueOnce({
      response: { status: 400, data: { detail: 'Ungültiger Inhalt' } },
    });

    render(
      <MemoryRouter>
        <MessagesPage />
      </MemoryRouter>
    );

    const input = await screen.findByTestId('message-input');
    await userEvent.type(input, 'Hallo');

    const sendBtn = screen.getByTestId('message-send-btn');
    await userEvent.click(sendBtn);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(expect.stringContaining('Nachricht konnte nicht gesendet werden'));
    });

    await waitFor(() => {
      expect(sendBtn).not.toBeDisabled();
    });
  });
});
