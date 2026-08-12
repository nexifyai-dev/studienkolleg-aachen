import React, { useState, useEffect } from 'react';
import apiClient from '../../lib/apiClient';

export const TARIFF_CATEGORIES = {
  kurs: 'Kurse',
  sprache: 'Sprache',
  pruefung: 'Pruefungen',
  gebuehr: 'Gebuehren',
  service: 'Services',
  unterkunft: 'Unterkunft',
  kombi: 'Kombi-Pakete',
  sonstig: 'Sonstiges',
};

/**
 * Tarif-Dropdown (Tarife = /api/products, verwaltet unter /admin/tariffs).
 * Wird in Angebots- und Rechnungserstellung genutzt.
 * - Lädt Tarife einmal beim Mount
 * - onAdd(tariff) wird beim Auswaehlen eines Tarifs aufgerufen
 */
export default function TariffSelect({ onAdd, label = 'Tarif auswaehlen', disabled = false }) {
  const [tariffs, setTariffs] = useState([]);
  const [value, setValue] = useState('');

  useEffect(() => {
    apiClient.get('/api/products', { withCredentials: true })
      .then(r => setTariffs(r.data || []))
      .catch(() => {});
  }, []);

  const grouped = tariffs.reduce((acc, t) => {
    const cat = t.category || 'sonstig';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(t);
    return acc;
  }, {});

  const handleChange = (e) => {
    const code = e.target.value;
    setValue('');
    if (!code) return;
    const tariff = tariffs.find(t => t.code === code);
    if (tariff && onAdd) onAdd(tariff);
  };

  return (
    <div className="w-full" data-testid="tariff-select">
      <label className="w2g-label mb-1">{label}</label>
      <select
        value={value}
        onChange={handleChange}
        disabled={disabled}
        className="w2g-select w-full text-xs py-2"
        data-testid="tariff-dropdown"
      >
        <option value="">— Tarif waehlen —</option>
        {Object.entries(grouped).map(([cat, list]) => (
          <optgroup key={cat} label={TARIFF_CATEGORIES[cat] || cat}>
            {list.map(t => (
              <option key={t.code} value={t.code}>
                {t.name} ({t.code}) – {new Intl.NumberFormat('de-DE', { style: 'currency', currency: t.currency || 'EUR' }).format(t.price || 0)}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );
}
