import { render, screen } from '@testing-library/react';
import App from './App';

test('renders public navigation on initial load', () => {
  render(<App />);
  expect(screen.getByTestId('nav-logo')).toBeInTheDocument();
});
