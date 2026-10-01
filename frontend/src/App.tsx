import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { Compare } from './pages/Compare';
import { Report } from './pages/Report';
import { ProductDetail } from './pages/Product';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
        <header className="bg-white shadow-sm sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex gap-6 items-center">
                <Link to="/" className="text-xl font-bold text-blue-600">Competitor Intel</Link>
                <nav className="hidden sm:flex gap-4">
                  <Link to="/" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
                  <Link to="/compare" className="text-gray-600 hover:text-gray-900">Compare</Link>
                  <Link to="/report" className="text-gray-600 hover:text-gray-900">AI Report</Link>
                </nav>
              </div>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/report" element={<Report />} />
            <Route path="/product/:id" element={<ProductDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
