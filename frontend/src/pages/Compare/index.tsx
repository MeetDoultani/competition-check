import { useState, useEffect } from 'react';
import { fetchComparison, fetchProducts } from '../../api/client';
import type { ComparisonMatrix, Product } from '../../types';

export function Compare() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [baselineId, setBaselineId] = useState<string>('');
  const [matrix, setMatrix] = useState<ComparisonMatrix | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchProducts().then(setProducts);
  }, []);

  const handleCompare = async () => {
    if (selectedIds.length < 2 || !baselineId) return;
    setLoading(true);
    try {
      const data = await fetchComparison(selectedIds, baselineId);
      setMatrix(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Compare Products</h1>
      
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
        <h2 className="text-lg font-semibold mb-4">Select Products to Compare (Min 2)</h2>
        <div className="flex flex-wrap gap-4 mb-4">
          {products?.map(p => (
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
              {selectedIds?.map(id => {
                const p = products?.find(x => x.id === id);
                return <option key={id} value={id}>{p?.name}</option>;
              })}
            </select>
          </div>
        )}

        <button 
          onClick={handleCompare}
          disabled={selectedIds.length < 2 || !baselineId || loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Matrix'}
        </button>
      </div>

      {!matrix && !loading ? (
        <div className="flex flex-col items-center justify-center py-16 text-gray-500 bg-white rounded-xl shadow-sm border border-gray-100">
          <p>Please select products to compare.</p>
        </div>
      ) : loading ? (
        <div className="flex flex-col items-center justify-center py-16 text-gray-500 bg-white rounded-xl shadow-sm border border-gray-100">
          <p>Loading comparison data...</p>
        </div>
      ) : matrix && matrix.attributes ? (
        <div className="overflow-x-auto bg-white rounded-xl shadow-sm border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Attribute</th>
                {matrix.products?.map(p => (
                  <th key={p.id} className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${p.id === matrix.baseline_product_id ? 'text-blue-600 bg-blue-50/50' : 'text-gray-500'}`}>
                    {p.name} {p.id === matrix.baseline_product_id ? '(Baseline)' : ''}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {matrix.attributes?.map((row) => (
                <tr key={row.attribute_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {row.attribute_name} {row.unit ? `(${row.unit})` : ''}
                  </td>
                  {matrix.products?.map(p => {
                    const cell = row.values?.find(v => v.product_id === p.id);
                    const isBaseline = p.id === matrix.baseline_product_id;
                    const val = cell && cell.value !== null ? cell.value : 'N/A';
                    const pct = cell?.delta?.percentage_change;
                    
                    return (
                      <td key={p.id} className={`px-6 py-4 whitespace-nowrap text-sm ${isBaseline ? 'bg-blue-50/20 font-semibold text-gray-900' : 'text-gray-500'}`}>
                        <div className="flex items-center gap-2">
                          <span>{String(val)}</span>
                          {!isBaseline && pct !== null && pct !== undefined && (
                            <span className={`text-xs px-2 py-1 rounded-full ${pct > 0 ? 'bg-green-100 text-green-800' : pct < 0 ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}>
                              {pct > 0 ? '+' : ''}{pct.toFixed(2)}%
                            </span>
                          )}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}
