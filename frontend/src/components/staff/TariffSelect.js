import React from 'react';

const CATEGORY_LABELS = {
  kurs: 'Kurse',
  sprache: 'Sprache',
  pruefung: 'Pruefungen',
  gebuehr: 'Gebuehren',
  service: 'Services',
  unterkunft: 'Unterkunft',
  kombi: 'Kombi-Pakete',
  sonstig: 'Sonstiges',
};

export const TariffSelect = ({ products, onSelect, testId = 'tariff-select' }) => {
  const grouped = {};
  (products || []).forEach(p => {
    const cat = p.category || 'sonstig';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(p);
  });

  const handleChange = (e) => {
    const product = (products || []).find(p => p.id === e.target.value);
    if (product) onSelect(product);
    e.target.value = '';
  };

  return (
    <select onChange={handleChange} defaultValue=""
      className="w2g-input text-xs py-1.5 cursor-pointer"
      data-testid={testId}>
      <option value="" disabled>Tarif auswählen und als Position hinzufügen...</option>
      {Object.entries(grouped).map(([cat, prods]) => (
        <optgroup key={cat} label={CATEGORY_LABELS[cat] || cat}>
          {prods.map(p => (
            <option key={p.id} value={p.id}>
              {p.name} — {p.price > 0 ? `${p.price.toLocaleString('de-DE')} EUR` : 'Individuell'}
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  );
};
