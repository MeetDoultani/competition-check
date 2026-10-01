export interface Brand {
  id: string;
  name: string;
}

export interface Category {
  id: string;
  name: string;
}

export interface ProductSpecification {
  id: string;
  attribute_name: string;
  value: string | number | boolean | null;
  unit: string | null;
  presence_state: string;
  evidence_snippet: string | null;
}

export interface Product {
  id: string;
  name: string;
  url: string;
  brand: Brand;
  category: Category;
  specifications: ProductSpecification[];
}

export interface SearchResult {
  product: Product;
  similarity_score: number;
}

export interface PricePoint {
  price: number;
  currency: string;
  observed_at: string;
}

export interface PriceHistoryResponse {
  product_id: string;
  history: PricePoint[];
}

export interface Citation {
  evidence_id: string;
  snippet: string;
}

export interface ReportSchema {
  executive_summary: string;
  key_differences: string[];
  pricing_analysis: string;
  potential_opportunities: string[];
  uncertainties_and_gaps: string[];
  evidence_citations: Citation[];
}

export interface ReportRequest {
  product_ids: string[];
  baseline_id: string;
}

export interface DeltaInfo {
  raw_diff: number | null;
  percentage_change: number | null;
}

export interface ProductAttributeValue {
  product_id: string;
  value: any;
  presence_state: string;
  evidence_snippet: string | null;
  delta: DeltaInfo | null;
}

export interface AttributeRow {
  attribute_id: string;
  attribute_name: string;
  data_type: string;
  unit: string | null;
  values: ProductAttributeValue[];
}

export interface ComparisonMatrix {
  baseline_product_id: string;
  products: Product[];
  attributes: AttributeRow[];
}
