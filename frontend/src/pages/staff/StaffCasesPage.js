import React, { useMemo, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Search, ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight, Zap, Loader2, CheckCircle, X } from 'lucide-react';
import { PageScaffold, ToolbarRow } from '../../components/layout/PageScaffold';
import { STAGE_LABELS, STAGE_COLORS, formatDate } from '../../lib/utils';
import { useApplications, useBatchScreening, useBatchStatus } from '../../lib/api-hooks';
import ViewToggle from '../../components/shared/ViewToggle';
import { toast } from 'sonner';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
} from '@tanstack/react-table';

const PAGE_SIZE = 15;

function SortIcon({ column }) {
  const sorted = column.getIsSorted();
  if (sorted === 'asc') return <ChevronUp size={12} />;
  if (sorted === 'desc') return <ChevronDown size={12} />;
  return <ChevronsUpDown size={12} className="opacity-40" />;
}

function BatchProgressBar({ batchId, onClose }) {
  const { data } = useBatchStatus(batchId);
  if (!data) return null;
  const { progress } = data;
  return (
    <div className="w2g-card p-3 flex items-center gap-3" data-testid="batch-progress-bar">
      <div className="w-[var(--icon-box)] h-[var(--icon-box)] flex items-center justify-center bg-[var(--color-primary-muted)]" style={{ borderRadius: 'var(--radius-sm)' }}>
        {progress.is_done ? <CheckCircle size={16} className="text-[var(--color-primary)]" /> : <Loader2 size={16} className="text-[var(--color-primary)] animate-spin" />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium text-[var(--color-text-primary)]">
            Batch-Screening {progress.is_done ? 'abgeschlossen' : 'laeuft...'}
          </span>
          <span className="text-xs text-[var(--color-text-tertiary)]">
            {progress.completed + progress.failed}/{progress.total}
          </span>
        </div>
        <div className="h-1.5 bg-[var(--color-surface-sunken)] overflow-hidden" style={{ borderRadius: 'var(--radius-sm)' }}>
          <div
            className="h-full bg-[var(--color-primary)] transition-all duration-300"
            style={{ width: `${progress.percent}%`, borderRadius: 'var(--radius-sm)' }}
          />
        </div>
        {progress.failed > 0 && (
          <span className="text-[10px] text-[var(--color-danger)] mt-0.5 block">{progress.failed} fehlgeschlagen</span>
        )}
      </div>
      {progress.is_done && (
        <button onClick={onClose} className="w2g-btn-icon" data-testid="batch-close-btn">
          <X size={14} />
        </button>
      )}
    </div>
  );
}

export default function StaffCasesPage() {
  const { t } = useTranslation();
  const { data: applications = [], isLoading } = useApplications();
  const [globalFilter, setGlobalFilter] = useState('');
  const [stageFilter, setStageFilter] = useState('all');
  const [sorting, setSorting] = useState([{ id: 'last_activity_at', desc: true }]);
  const [viewMode, setViewMode] = useState('list');
  const [rowSelection, setRowSelection] = useState({});
  const [batchId, setBatchId] = useState(null);

  const batchScreening = useBatchScreening();

  const filtered = useMemo(() => {
    if (stageFilter === 'all') return applications;
    return applications.filter(a => a.current_stage === stageFilter);
  }, [applications, stageFilter]);

  const columns = useMemo(() => [
    {
      id: 'select',
      header: ({ table }) => (
        <input
          type="checkbox"
          checked={table.getIsAllPageRowsSelected()}
          onChange={table.getToggleAllPageRowsSelectedHandler()}
          className="w2g-checkbox"
          data-testid="batch-select-all"
        />
      ),
      cell: ({ row }) => (
        <input
          type="checkbox"
          checked={row.getIsSelected()}
          onChange={row.getToggleSelectedHandler()}
          className="w2g-checkbox"
          data-testid={`batch-select-${row.original.id}`}
        />
      ),
      enableSorting: false,
      size: 36,
    },
    {
      accessorKey: 'applicant.full_name',
      id: 'name',
      header: t('staff.cases.applicant', 'Fall'),
      accessorFn: row => row.applicant?.full_name || t('common.none', 'Unbekannt'),
      cell: ({ row }) => {
        const app = row.original;
        return (
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-[var(--color-text-primary)]">{app.applicant?.full_name || t('common.none', 'Unbekannt')}</span>
              {app.duplicate_flag && (
                <span className="text-[8px] px-1.5 py-0.5 rounded bg-[var(--color-danger-bg)] text-[var(--color-danger)] font-bold border border-[var(--color-danger-border)]" data-testid={`duplicate-badge-${app.id}`}>
                  DUBLETTE
                </span>
              )}
            </div>
            <div className="text-xs text-[var(--color-text-secondary)] flex items-center gap-2">
              {app.applicant_number && <span className="font-mono text-[var(--color-primary)] font-bold" data-testid="case-applicant-number">{app.applicant_number}</span>}
              <span>{app.applicant?.email || 'Keine E-Mail'}</span>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'course_type',
      header: t('staff.cases.stage', 'Bereich'),
      cell: ({ getValue }) => (
        <span className="text-sm text-[var(--color-text-secondary)]">{getValue() || 'Nicht zugeordnet'}</span>
      ),
    },
    {
      accessorKey: 'current_stage',
      header: t('staff.cases.stage', 'Status'),
      cell: ({ getValue }) => {
        const stage = getValue();
        return (
          <span className={`w2g-badge ${STAGE_COLORS[stage] || 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>
            {STAGE_LABELS[stage] || stage}
          </span>
        );
      },
    },
    {
      accessorKey: 'degree_country',
      header: t('staff.detail.country_degree', 'Land'),
      cell: ({ getValue }) => (
        <span className="text-sm text-[var(--color-text-secondary)]">{getValue() || '\u2014'}</span>
      ),
    },
    {
      accessorKey: 'last_activity_at',
      header: t('staff.cases.last_activity', 'Letzte Aktivitaet'),
      cell: ({ getValue }) => (
        <span className="text-sm text-[var(--color-text-secondary)]">{formatDate(getValue())}</span>
      ),
      sortingFn: (a, b) => {
        const dA = new Date(a.original.last_activity_at || a.original.created_at || 0);
        const dB = new Date(b.original.last_activity_at || b.original.created_at || 0);
        return dA - dB;
      },
    },
    {
      id: 'actions',
      header: '',
      cell: ({ row }) => (
        <Link to={`/staff/applications/${row.original.id}`}
          className="w2g-btn-table-action"
          data-testid={`staff-case-open-${row.original.id}`}>
          Oeffnen
        </Link>
      ),
      enableSorting: false,
    },
  ], []);

  const table = useReactTable({
    data: filtered,
    columns,
    state: { sorting, globalFilter, rowSelection },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    onRowSelectionChange: setRowSelection,
    enableRowSelection: true,
    globalFilterFn: (row, _columnId, filterValue) => {
      const q = filterValue.toLowerCase();
      const name = (row.original.applicant?.full_name || '').toLowerCase();
      const email = (row.original.applicant?.email || '').toLowerCase();
      const country = (row.original.degree_country || '').toLowerCase();
      const appNum = (row.original.applicant_number || '').toLowerCase();
      const phone = (row.original.applicant?.phone || '').toLowerCase();
      const course = (row.original.course_type || '').toLowerCase();
      return name.includes(q) || email.includes(q) || country.includes(q) || appNum.includes(q) || phone.includes(q) || course.includes(q);
    },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: PAGE_SIZE } },
  });

  const selectedCount = Object.keys(rowSelection).length;
  const selectedIds = useMemo(() => {
    return table.getSelectedRowModel().rows.map(r => r.original.id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [table, rowSelection]);

  const handleBatchScreening = useCallback(() => {
    if (selectedIds.length === 0) return;
    batchScreening.mutate(selectedIds, {
      onSuccess: (data) => {
        setBatchId(data.batch_id);
        setRowSelection({});
        toast.success(`Batch-Screening gestartet: ${data.enqueued} Bewerbungen`);
        if (data.skipped?.length > 0) {
          toast.info(`${data.skipped.length} uebersprungen`);
        }
      },
      onError: (err) => {
        toast.error(err.response?.data?.detail || 'Batch-Screening fehlgeschlagen');
      },
    });
  }, [selectedIds, batchScreening]);

  const pageIndex = table.getState().pagination.pageIndex;
  const pageCount = table.getPageCount();

  return (
    <PageScaffold
      title={t('staff.cases.title', 'Fallliste')}
      subtitle={`${table.getFilteredRowModel().rows.length} von ${applications.length} ${t('staff.cases.total', 'Faellen')}${stageFilter !== 'all' ? ` (${STAGE_LABELS[stageFilter] || stageFilter})` : ''}`}
      testId="staff-cases-page"
      toolbar={
        <ToolbarRow
          search={
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
              <input
                value={globalFilter}
                onChange={e => setGlobalFilter(e.target.value)}
                className="w2g-search pl-10"
                placeholder={t('staff.cases.search_placeholder', 'Name, E-Mail, Telefon, Nr. oder Land...')}
                data-testid="staff-cases-search"
              />
            </div>
          }
          filters={[
            <select
              key="stage"
              value={stageFilter}
              onChange={e => setStageFilter(e.target.value)}
              className="w2g-select"
              data-testid="staff-cases-stage-filter"
            >
              <option value="all">{t('staff.cases.all_stages', 'Alle Status')}</option>
              {Object.entries(STAGE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>,
          ]}
          extra={
            <div className="flex items-center gap-2">
              {selectedCount > 0 && (
                <button
                  onClick={handleBatchScreening}
                  disabled={batchScreening.isPending}
                  className="w2g-btn-primary flex items-center gap-1.5 text-xs"
                  data-testid="batch-screening-btn"
                >
                  {batchScreening.isPending ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
                  Batch-Screening ({selectedCount})
                </button>
              )}
              <ViewToggle view={viewMode} onChange={setViewMode} />
            </div>
          }
        />
      }
    >
      {batchId && (
        <div className="mb-4">
          <BatchProgressBar batchId={batchId} onClose={() => setBatchId(null)} />
        </div>
      )}

      {isLoading ? (
        <div className="w2g-loading" data-testid="staff-cases-loading">
          <div className="w2g-spinner" />
        </div>
      ) : (
        <>
          {viewMode === 'list' ? (
          <div className="w2g-card p-0 overflow-hidden" data-testid="staff-cases-table-wrapper">
            <div className="overflow-x-auto">
              <table className="w2g-table" data-testid="staff-cases-table">
                <thead>
                  {table.getHeaderGroups().map(hg => (
                    <tr key={hg.id}>
                      {hg.headers.map(header => (
                        <th
                          key={header.id}
                          className={header.column.getCanSort() ? 'cursor-pointer select-none' : ''}
                          onClick={header.column.getToggleSortingHandler()}
                          data-testid={`col-header-${header.id}`}
                          style={header.column.id === 'select' ? { width: 36 } : undefined}
                        >
                          <div className="flex items-center gap-1">
                            {flexRender(header.column.columnDef.header, header.getContext())}
                            {header.column.getCanSort() && <SortIcon column={header.column} />}
                          </div>
                        </th>
                      ))}
                    </tr>
                  ))}
                </thead>
                <tbody>
                  {table.getRowModel().rows.length === 0 ? (
                    <tr>
                      <td colSpan={columns.length} className="text-center py-12 text-sm text-[var(--color-text-tertiary)]">
                        {globalFilter ? 'Keine Treffer fuer diese Suche.' : 'Keine Faelle vorhanden.'}
                      </td>
                    </tr>
                  ) : (
                    table.getRowModel().rows.map(row => (
                      <tr key={row.id} data-testid={`staff-case-row-${row.original.id}`}
                        className={row.getIsSelected() ? 'bg-[var(--color-primary-muted)]' : ''}>
                        {row.getVisibleCells().map(cell => (
                          <td key={cell.id}>
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </td>
                        ))}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
          ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="staff-cases-grid">
            {table.getRowModel().rows.length === 0 ? (
              <div className="col-span-full text-center py-12 text-sm text-[var(--color-text-tertiary)]">
                {globalFilter ? 'Keine Treffer fuer diese Suche.' : 'Keine Faelle vorhanden.'}
              </div>
            ) : (
              table.getRowModel().rows.map(row => {
                const app = row.original;
                const initials = (app.applicant?.full_name || '?').split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
                return (
                  <Link key={row.id} to={`/staff/applications/${app.id}`}
                    className="w2g-card-interactive p-0 overflow-hidden" data-testid={`staff-case-card-${app.id}`}>
                    <div className="p-4">
                      <div className="flex items-start gap-3 mb-3">
                        <div className="w-10 h-10 bg-[var(--color-primary)] flex items-center justify-center text-white text-xs font-bold shrink-0" style={{ borderRadius: 'var(--radius-sm)' }}>
                          {initials}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-bold text-[var(--color-text-primary)] truncate">{app.applicant?.full_name || 'Unbekannt'}</p>
                          <p className="text-[11px] text-[var(--color-text-tertiary)] truncate">{app.applicant?.email || '\u2013'}</p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className={`w2g-badge text-[10px] ${STAGE_COLORS[app.current_stage] || 'bg-[var(--color-surface-sunken)] text-[var(--color-text-secondary)]'}`}>
                          {STAGE_LABELS[app.current_stage] || app.current_stage}
                        </span>
                        <span className="text-[10px] text-[var(--color-text-tertiary)]">{app.course_type || '\u2013'}</span>
                      </div>
                    </div>
                    <div className="border-t border-[var(--color-divider-subtle)] px-4 py-2 flex items-center justify-between text-[10px] text-[var(--color-text-tertiary)]">
                      <span>{app.degree_country || '\u2013'}</span>
                      <span>{formatDate(app.last_activity_at || app.created_at)}</span>
                    </div>
                  </Link>
                );
              })
            )}
          </div>
          )}

          {/* Pagination */}
          {pageCount > 1 && (
            <div className="flex items-center justify-between mt-4 px-1" data-testid="cases-pagination">
              <span className="text-xs text-[var(--color-text-tertiary)]">
                Seite {pageIndex + 1} von {pageCount} ({table.getFilteredRowModel().rows.length} Eintraege)
              </span>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => table.previousPage()}
                  disabled={!table.getCanPreviousPage()}
                  className="w2g-btn-icon disabled:opacity-30"
                  data-testid="cases-prev-page"
                >
                  <ChevronLeft size={14} />
                </button>
                {Array.from({ length: Math.min(pageCount, 7) }, (_, i) => {
                  let page = i;
                  if (pageCount > 7) {
                    if (pageIndex < 4) page = i;
                    else if (pageIndex > pageCount - 5) page = pageCount - 7 + i;
                    else page = pageIndex - 3 + i;
                  }
                  return (
                    <button
                      key={page}
                      onClick={() => table.setPageIndex(page)}
                      className={`min-w-[28px] h-7 text-xs font-medium transition-colors ${
                        page === pageIndex
                          ? 'bg-[var(--color-primary)] text-white'
                          : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-elevated)]'
                      }`}
                      style={{ borderRadius: 'var(--radius-sm)' }}
                      data-testid={`cases-page-${page}`}
                    >
                      {page + 1}
                    </button>
                  );
                })}
                <button
                  onClick={() => table.nextPage()}
                  disabled={!table.getCanNextPage()}
                  className="w2g-btn-icon disabled:opacity-30"
                  data-testid="cases-next-page"
                >
                  <ChevronRight size={14} />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </PageScaffold>
  );
}
