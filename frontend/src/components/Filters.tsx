import React from 'react';

interface FiltersProps {
  industryFilter: string;
  sizeFilter: number;
  maxCompanySize: number;
  onIndustryChange: (industry: string) => void;
  onSizeChange: (size: number) => void;
}

const industries = [
  'Technology',
  'Healthcare',
  'Finance',
  'Manufacturing',
  'Retail',
  'Education',
  'Real Estate',
  'Consulting'
];

const Filters: React.FC<FiltersProps> = ({
  industryFilter,
  sizeFilter,
  maxCompanySize,
  onIndustryChange,
  onSizeChange
}) => {
  // Calculate dynamic maximum: database max + 200, with a minimum of 500
  const dynamicMax = Math.max(maxCompanySize + 200, 500);
  
  // Calculate appropriate step size based on the maximum
  const stepSize = dynamicMax <= 1000 ? 25 : Math.ceil(dynamicMax / 100);

  return (
    <div style={{
      display: 'flex',
      gap: '20px',
      alignItems: 'center',
      marginBottom: '30px',
      padding: '20px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
        <label style={{ fontWeight: 'bold', color: '#333' }}>Industry:</label>
        <select
          value={industryFilter}
          onChange={(e) => onIndustryChange(e.target.value)}
          style={{
            padding: '8px 12px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '14px',
            minWidth: '150px'
          }}
        >
          <option value="">All Industries</option>
          {industries.map(industry => (
            <option key={industry} value={industry}>
              {industry}
            </option>
          ))}
        </select>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
        <label style={{ fontWeight: 'bold', color: '#333' }}>
          Company Size: {sizeFilter === 0 ? 'All' : `${sizeFilter}+ employees`}
        </label>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input
            type="range"
            min="0"
            max={dynamicMax}
            step={stepSize}
            value={Math.min(sizeFilter, dynamicMax)} // Ensure current value doesn't exceed new max
            onChange={(e) => onSizeChange(Number(e.target.value))}
            style={{ width: '200px' }}
          />
          <input
            type="number"
            min="0"
            max={dynamicMax}
            step={stepSize}
            value={sizeFilter}
            onChange={(e) => onSizeChange(Math.min(Number(e.target.value), dynamicMax))}
            style={{
              width: '80px',
              padding: '4px 8px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px'
            }}
          />
        </div>
        {maxCompanySize > 0 && (
          <div style={{ fontSize: '12px', color: '#666', marginTop: '2px' }}>
            Max company size in database: {maxCompanySize} employees
          </div>
        )}
      </div>
    </div>
  );
};

export default Filters;