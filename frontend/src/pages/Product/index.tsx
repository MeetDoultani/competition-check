import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchProduct, fetchPriceHistory } from '../../api/client';
import type { Product, PriceHistoryResponse } from '../../types';
import { PriceChart } from '../../components/charts/PriceChart';
import { ArrowLeft } from 'lucide-react';

export function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [history, setHistory] = useState<PriceHistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    Promise.all([fetchProduct(id), fetchPriceHistory(id)])
      .then(([pData, hData]) => {
        setProduct(pData);
        setHistory(hData);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (!product) return <div>Product not found.</div>;

  return (
    <div className="max-w-5xl mx-auto">
      <Link to="/" className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-6">
        <ArrowLeft size={16} className="mr-2" /> Back to Dashboard
      </Link>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
            <div className="text-sm font-semibold text-blue-600 mb-1">{product.brand.name}</div>
            <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
            <div className="text-gray-500 mb-6">{product.category.name}</div>
            
            <h3 className="text-lg font-semibold border-b pb-2 mb-4">Specifications</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {product.specifications.map(s => (
                <div key={s.id} className="bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">{s.attribute_name}</div>
                  <div className="font-medium text-gray-900">
                    {String(s.value)} {s.unit || ''}
                  </div>
                  {s.evidence_snippet && (
                    <div className="mt-2 text-xs text-gray-400 italic">"{s.evidence_snippet}"</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold mb-2">Price History</h3>
            {history && history.history.length > 0 ? (
              <PriceChart data={history.history} />
            ) : (
              <div className="text-sm text-gray-500 mt-4">No historical pricing data available.</div>
            )}
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold mb-4">Source Link</h3>
            <a href={product.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">
              {product.url}
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
