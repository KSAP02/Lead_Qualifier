import React, { useState } from 'react';
import type { Lead } from '../services/api';

interface LeadTableProps {
  leads: Lead[];
}

const LeadTable: React.FC<LeadTableProps> = ({ leads }) => {
  const [hoveredLead, setHoveredLead] = useState<Lead | null>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const getQualityColor = (quality: string) => {
    switch (quality.toLowerCase()) {
      case 'high': return '#28a745';
      case 'medium': return '#ffc107';
      case 'low': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const handleMouseEnter = (lead: Lead, event: React.MouseEvent) => {
    setHoveredLead(lead);
    updateMousePosition(event);
  };

  const handleMouseMove = (event: React.MouseEvent) => {
    updateMousePosition(event);
  };

  const updateMousePosition = (event: React.MouseEvent) => {
    const tooltipWidth = 400; // Max width of tooltip
    const tooltipHeight = 250; // Approximate height of tooltip
    const margin = 20; // Margin from screen edges
    
    let x = event.clientX + 15;
    let y = event.clientY - 10;
    
    // Adjust horizontal position if tooltip would go off-screen
    if (x + tooltipWidth > window.innerWidth - margin) {
      x = event.clientX - tooltipWidth - 15;
    }
    
    // Adjust vertical position if tooltip would go off-screen
    if (y + tooltipHeight > window.innerHeight - margin) {
      y = event.clientY - tooltipHeight + 10;
    }
    
    // Ensure tooltip doesn't go above the top of the screen
    if (y < margin) {
      y = margin;
    }
    
    setMousePosition({ x, y });
  };

  const handleMouseLeave = () => {
    setHoveredLead(null);
  };

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      overflow: 'hidden',
      position: 'relative'
    }}>
      <div style={{
        padding: '20px',
        borderBottom: '1px solid #dee2e6',
        backgroundColor: '#f8f9fa'
      }}>
        <h3 style={{ margin: 0, color: '#333' }}>
          Leads ({leads.length})
        </h3>
      </div>
      
      {leads.length === 0 ? (
        <div style={{ padding: '40px', textAlign: 'center', color: '#6c757d' }}>
          No leads found matching your criteria
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f8f9fa' }}>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Name</th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Company</th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Industry</th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Size</th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Source</th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Created</th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Quality</th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Summary</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead, index) => (
                <tr 
                  key={lead.id || index} 
                  style={{ 
                    borderBottom: '1px solid #f8f9fa',
                    cursor: 'pointer',
                    backgroundColor: hoveredLead?.id === lead.id ? '#f8f9fa' : 'transparent',
                    transition: 'background-color 0.2s ease'
                  }}
                  onMouseEnter={(e) => handleMouseEnter(lead, e)}
                  onMouseMove={handleMouseMove}
                  onMouseLeave={handleMouseLeave}
                >
                  <td style={{ padding: '12px' }}>{lead.name}</td>
                  <td style={{ padding: '12px' }}>{lead.company}</td>
                  <td style={{ padding: '12px' }}>{lead.industry}</td>
                  <td style={{ padding: '12px' }}>{lead.size}</td>
                  <td style={{ padding: '12px' }}>{lead.source}</td>
                  <td style={{ padding: '12px' }}>
                    {new Date(lead.created_at).toLocaleDateString()}
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      color: 'white',
                      backgroundColor: getQualityColor(lead.quality)
                    }}>
                      {lead.quality}
                    </span>
                  </td>
                  <td style={{ padding: '12px', maxWidth: '200px' }}>
                    <div style={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {lead.summary}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tooltip */}
      {hoveredLead && (
        <div style={{
          position: 'fixed',
          left: mousePosition.x + 15,
          top: mousePosition.y - 10,
          backgroundColor: 'rgba(0, 0, 0, 0.9)',
          color: 'white',
          padding: '16px',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          zIndex: 1000,
          maxWidth: '400px',
          fontSize: '14px',
          lineHeight: '1.4',
          pointerEvents: 'none'
        }}>
          <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '16px' }}>
            {hoveredLead.name}
          </div>
          <div style={{ marginBottom: '4px' }}>
            <strong>Company:</strong> {hoveredLead.company}
          </div>
          <div style={{ marginBottom: '4px' }}>
            <strong>Industry:</strong> {hoveredLead.industry}
          </div>
          <div style={{ marginBottom: '4px' }}>
            <strong>Size:</strong> {hoveredLead.size}
          </div>
          <div style={{ marginBottom: '4px' }}>
            <strong>Source:</strong> {hoveredLead.source}
          </div>
          <div style={{ marginBottom: '4px' }}>
            <strong>Created:</strong> {new Date(hoveredLead.created_at).toLocaleDateString()}
          </div>
          <div style={{ marginBottom: '8px' }}>
            <strong>Quality:</strong> 
            <span style={{
              marginLeft: '8px',
              padding: '2px 6px',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: 'bold',
              backgroundColor: getQualityColor(hoveredLead.quality)
            }}>
              {hoveredLead.quality}
            </span>
          </div>
          <div>
            <strong>Summary:</strong>
            <div style={{ marginTop: '4px', fontStyle: 'italic' }}>
              {hoveredLead.summary}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LeadTable;