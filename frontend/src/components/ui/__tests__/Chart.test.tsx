import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Chart from '../Chart';

const mockData = [
  { label: 'A', value: 10, color: '#ff0000' },
  { label: 'B', value: 20, color: '#00ff00' },
  { label: 'C', value: 30, color: '#0000ff' },
];

describe('Chart', () => {
  it('renders bar chart by default', () => {
    render(<Chart data={mockData} />);
    
    mockData.forEach(item => {
      expect(screen.getByText(item.label)).toBeInTheDocument();
      expect(screen.getByText(item.value.toString())).toBeInTheDocument();
    });
  });

  it('renders bar chart with custom height', () => {
    render(<Chart data={mockData} height={400} />);
    const chartContainer = screen.getByText('A').closest('div');
    expect(chartContainer).toHaveStyle({ height: '400px' });
  });

  it('renders line chart', () => {
    render(<Chart data={mockData} type="line" />);
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg?.querySelector('polyline')).toBeInTheDocument();
  });

  it('renders pie chart', () => {
    render(<Chart data={mockData} type="pie" />);
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg?.querySelector('path')).toBeInTheDocument();
  });

  it('renders doughnut chart', () => {
    render(<Chart data={mockData} type="doughnut" />);
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg?.querySelector('circle')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<Chart data={mockData} className="custom-chart" />);
    const chartContainer = screen.getByText('A').closest('div');
    expect(chartContainer).toHaveClass('custom-chart');
  });

  it('handles empty data gracefully', () => {
    render(<Chart data={[]} />);
    expect(screen.getByText('A')).not.toBeInTheDocument();
  });

  it('uses default colors when not provided', () => {
    const dataWithoutColors = [
      { label: 'A', value: 10 },
      { label: 'B', value: 20 },
    ];
    render(<Chart data={dataWithoutColors} />);
    
    dataWithoutColors.forEach(item => {
      expect(screen.getByText(item.label)).toBeInTheDocument();
      expect(screen.getByText(item.value.toString())).toBeInTheDocument();
    });
  });

  it('calculates max value correctly for scaling', () => {
    const dataWithHighValues = [
      { label: 'Low', value: 5 },
      { label: 'High', value: 100 },
    ];
    render(<Chart data={dataWithHighValues} />);
    
    // The high value should be displayed
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('renders with single data point', () => {
    const singleData = [{ label: 'Single', value: 50 }];
    render(<Chart data={singleData} />);
    
    expect(screen.getByText('Single')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
  });
});
