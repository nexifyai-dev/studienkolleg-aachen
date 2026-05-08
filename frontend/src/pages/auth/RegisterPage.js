import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

/**
 * RegisterPage redirects to /apply.
 * Registrierung ohne Bewerbung ergibt keinen Sinn im Gesamtkonzept.
 * Die Bewerbungsseite (ApplyPage) erstellt automatisch einen Portal-Zugang.
 */
export default function RegisterPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const inviteToken = searchParams.get('token');

  useEffect(() => {
    const target = inviteToken ? `/apply?token=${inviteToken}` : '/apply';
    navigate(target, { replace: true });
  }, [navigate, inviteToken]);

  return null;
}
