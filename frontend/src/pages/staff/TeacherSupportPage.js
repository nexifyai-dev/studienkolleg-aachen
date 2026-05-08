import React from 'react';
import { SupportConversationPanel } from '../../components/shared/SupportConversationPanel';

export default function TeacherSupportPage() {
  return (
    <SupportConversationPanel
      title="Nachrichten"
      subtitle="Lehrbezogene Rückfragen laufen über einen klaren, dokumentierten Supportkanal mit Kontext rechts und stabiler Chatmitte."
      testId="teacher-support-page"
      quickTopics={['Kursstatus klären', 'Feedback abstimmen', 'Termin organisieren']}
      contextBlocks={[
        { title: 'Status', items: [{ label: 'Rolle', value: 'Teacher' }, { label: 'Zugriff', value: 'Nur zugewiesene Lernende' }] },
        { title: 'Nächste empfohlene Aktion', items: [{ label: 'Empfehlung', value: 'Kursstatus oder Rückmeldung mit dem Staff-Team synchronisieren.' }] },
      ]}
      actionLinks={[{ to: '/staff/students', label: 'Zu Lernenden' }, { to: '/staff', label: 'Zum Dashboard' }]}
    />
  );
}
