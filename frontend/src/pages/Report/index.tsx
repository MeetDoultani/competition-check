import { useState, useEffect } from 'react';
import { generateReport, fetchProducts } from '../../api/client';
import type { ReportSchema, Product } from '../../types';

export function Report() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [baselineId, setBaselineId] = useState<string>('');
  const [report, setReport] = useState<ReportSchema | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProducts().then(setProducts);
  }, []);

  const handleGenerate = async () => {
    if (selectedIds.length < 2 || !baselineId) return;
    setLoading(true);
    try {
      const data = await generateReport({ product_ids: selectedIds, baseline_id: baselineId });
      setReport(data);
    } finally {
      setLoading(false);
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">AI Intelligence Report</h1>
      
      {!report && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
          <h2 className="text-lg font-semibold mb-4">Select Products for Analysis</h2>
          <div className="flex flex-wrap gap-4 mb-4">
            {products.map(p => (
              <label key={p.id} className="flex items-center gap-2 cursor-pointer bg-gray-50 px-4 py-2 rounded-lg border border-gray-200">
                <input type="checkbox" checked={selectedIds.includes(p.id)} onChange={() => toggleSelect(p.id)} className="w-4 h-4 text-blue-600 rounded" />
                <span>{p.name}</span>
              </label>
            ))}
          </div>
          
          {selectedIds.length >= 2 && (
            <div className="mb-4">
              <h2 className="text-sm font-semibold mb-2">Select Baseline:</h2>
              <select value={baselineId} onChange={(e) => setBaselineId(e.target.value)} className="border border-gray-300 rounded p-2">
                <option value="">-- Select Baseline --</option>
                {selectedIds.map(id => {
                  const p = products.find(x => x.id === id);
                  return <option key={id} value={id}>{p?.name}</option>;
                })}
              </select>
            </div>
          )}

          <button 
            onClick={handleGenerate}
            disabled={selectedIds.length < 2 || !baselineId || loading}
            className="bg-purple-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? 'Synthesizing...' : 'Generate Report'}
          </button>
        </div>
      )}

      {report && (
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 prose max-w-none">
          <h2>Executive Summary</h2>
          <p>{report.executive_summary}</p>
          
          <h2>Pricing Analysis</h2>
          <p>{report.pricing_analysis}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 my-8">
            <div>
              <h3>Key Differences</h3>
              <ul>
                {report.key_differences.map((k, i) => <li key={i}>{k}</li>)}
              </ul>
            </div>
            <div>
              <h3>Opportunities</h3>
              <ul>
                {report.potential_opportunities.map((k, i) => <li key={i}>{k}</li>)}
              </ul>
            </div>
          </div>
          
          <h3>Uncertainties & Gaps</h3>
          <ul>
            {report.uncertainties_and_gaps.map((k, i) => <li key={i}>{k}</li>)}
          </ul>

          <div className="mt-12 pt-8 border-t border-gray-200">
            <h4 className="text-gray-500 text-sm uppercase tracking-wider mb-4">Evidence Citations</h4>
            <div className="text-sm text-gray-600 space-y-2">
              {report.evidence_citations.map((c, i) => (
                <div key={i} className="bg-gray-50 p-3 rounded">
                  <span className="font-semibold block mb-1">Source {c.evidence_id}:</span>
                  <span className="italic">"{c.snippet}"</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
