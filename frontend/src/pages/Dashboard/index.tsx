import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search } from 'lucide-react';
import { fetchProducts, searchProducts } from '../../api/client';
import type { Product } from '../../types';

export function Dashboard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        if (!query.trim()) {
          const data = await fetchProducts();
          setProducts(data);
        } else {
          const results = await searchProducts(query);
          setProducts(results.map(r => r.product));
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
  };

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Product Catalog</h1>
      </div>
      
      <form onSubmit={handleSearch} className="mb-8 max-w-xl relative">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input 
            type="text" 
            placeholder="Search semantics (e.g. noise cancelling headphones)..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none shadow-sm"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </form>

      {loading ? (
        <div className="text-gray-500">Loading catalog...</div>
      ) : products.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-500 bg-white rounded-xl shadow-sm border border-gray-100">
          <Search className="w-12 h-12 mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900">No products found</h3>
          <p className="mt-1">We couldn't find any products matching your semantic search.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map(p => (
            <Link key={p.id} to={`/product/${p.id}`} className="block bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
              <div className="text-sm font-semibold text-blue-600 mb-1">{p.brand.name}</div>
              <h2 className="text-xl font-bold mb-2">{p.name}</h2>
              <div className="text-sm text-gray-500">{p.category.name}</div>
              <div className="mt-4 flex flex-wrap gap-2">
                {p.specifications.slice(0, 3).map(s => (
                  <span key={s.id} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {s.attribute_name}: {s.value}{s.unit ? ` ${s.unit}` : ''}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
