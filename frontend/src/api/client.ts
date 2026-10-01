import type { Product, SearchResult, PriceHistoryResponse, ReportSchema, ReportRequest, ComparisonMatrix } from '../types';

export const fetchProducts = async (skip = 0, limit = 20): Promise<Product[]> => {
  const res = await fetch(`/api/v1/products/?skip=${skip}&limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch products');
  return res.json();
};

export const fetchProduct = async (id: string): Promise<Product> => {
  const res = await fetch(`/api/v1/products/${id}`);
  if (!res.ok) throw new Error('Failed to fetch product');
  return res.json();
};

export const searchProducts = async (query: string, limit = 5): Promise<SearchResult[]> => {
  const res = await fetch(`/api/v1/search/?query=${encodeURIComponent(query)}&limit=${limit}`);
  if (!res.ok) throw new Error('Failed to search products');
  return res.json();
};

export const fetchComparison = async (productIds: string[], baselineId: string): Promise<ComparisonMatrix> => {
  const queryParams = productIds.map(id => `product_ids=${id}`).join('&');
  const res = await fetch(`/api/v1/compare/?${queryParams}&baseline_id=${baselineId}`);
  if (!res.ok) throw new Error('Failed to fetch comparison');
  return res.json();
};

export const fetchPriceHistory = async (productId: string): Promise<PriceHistoryResponse> => {
  const res = await fetch(`/api/v1/prices/${productId}/price-history`);
  if (!res.ok) throw new Error('Failed to fetch price history');
  return res.json();
};

export const generateReport = async (req: ReportRequest): Promise<ReportSchema> => {
  const res = await fetch('/api/v1/reports/compare/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error('Failed to generate report');
  return res.json();
};
