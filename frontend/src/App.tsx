import React, { useState, useEffect } from 'react';
import Filters from './components/Filters';
import LeadTable from './components/LeadTable';
import LeadChart from './components/LeadChart';
import { getLeads, postEvent } from './services/api';
import type { Lead } from './services/api';

type ViewType = 'table' | 'chart';

const App: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [industryFilter, setIndustryFilter] = useState<string>('');
  const [sizeFilter, setSizeFilter] = useState<number>(0);
  const [viewType, setViewType] = useState<ViewType>('table');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const fetchLeads = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getLeads(
        industryFilter || undefined,
        sizeFilter || undefined
      );
      setLeads(data);
    } catch (err) {
      setError('Failed to fetch leads');
      console.error('Error fetching leads:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, [industryFilter, sizeFilter]);

  const handleIndustryChange = (industry: string) => {
    setIndustryFilter(industry);
    postEvent({
      action: 'filter',
      data: { type: 'industry', value: industry }
    }).catch(console.error);
  };

  const handleSizeChange = (size: number) => {
    setSizeFilter(size);
    postEvent({
      action: 'filter',
      data: { type: 'size', value: size }
    }).catch(console.error);
  };

  const handleViewToggle = (view: ViewType) => {
    setViewType(view);
    postEvent({
      action: 'toggle_view',
      data: { view }
    }).catch(console.error);
  };

  const handleRefresh = () => {
    fetchLeads();
    postEvent({
      action: 'refresh',
      data: { timestamp: new Date().toISOString() }
    }).catch(console.error);
  };

  // Calculate maximum company size from current leads data
  const calculateMaxCompanySize = (leads: Lead[]) => {
    if (leads.length === 0) return 0;
    
    return Math.max(...leads.map(lead => {
      // Extract numbers from the size field (handles formats like "50-100", "500+", "100 employees", etc.)
      const sizeStr = lead.size?.toString() || '0';
      const numbers = sizeStr.match(/\d+/g);
      
      if (!numbers) return 0;
      
      // If there are multiple numbers (like "50-100"), take the larger one
      return Math.max(...numbers.map(num => parseInt(num, 10)));
    }));
  };

  const maxCompanySize = calculateMaxCompanySize(leads);

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ marginBottom: '30px' }}>
        <h1 style={{ color: '#333', marginBottom: '10px' }}>Lead Qualifier Dashboard</h1>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={() => handleViewToggle('table')}
            style={{
              padding: '8px 16px',
              backgroundColor: viewType === 'table' ? '#007bff' : '#f8f9fa',
              color: viewType === 'table' ? 'white' : '#333',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Table View
          </button>
          <button
            onClick={() => handleViewToggle('chart')}
            style={{
              padding: '8px 16px',
              backgroundColor: viewType === 'chart' ? '#007bff' : '#f8f9fa',
              color: viewType === 'chart' ? 'white' : '#333',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Chart View
          </button>
          <button
            onClick={handleRefresh}
            style={{
              padding: '8px 16px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Refresh
          </button>
        </div>
      </header>

      <Filters
        industryFilter={industryFilter}
        sizeFilter={sizeFilter}
        maxCompanySize={maxCompanySize}  // Add this line
        onIndustryChange={handleIndustryChange}
        onSizeChange={handleSizeChange}
      />

      {error && (
        <div style={{
          padding: '10px',
          marginBottom: '20px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '4px'
        }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div>Loading leads...</div>
        </div>
      ) : (
        <>
          {viewType === 'table' ? (
            <LeadTable leads={leads} />
          ) : (
            <LeadChart leads={leads} chartType="pie" />
          )}
        </>
      )}
    </div>
  );
};

export default App;
