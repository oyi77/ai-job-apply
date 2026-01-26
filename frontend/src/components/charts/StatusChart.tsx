import React, { useState } from 'react';
import Chart, { ChartProps } from '../ui/Chart';
import Select from '../ui/Select';

interface StatusChartProps {
  data: ChartProps['data'];
}

export const StatusChart: React.FC<StatusChartProps> = ({ data }) => {
  const [chartType, setChartType] = useState('bar');

  const chartTypeOptions = [
    { value: 'bar', label: 'Bar Chart' },
    { value: 'line', label: 'Line Chart' },
    { value: 'pie', label: 'Pie Chart' },
    { value: 'doughnut', label: 'Doughnut Chart' },
  ];

  return (
    <>
      <div className="flex space-x-3 mb-4">
        <Select
          name="chartType"
          value={chartType}
          onChange={(value) => setChartType(value as string)}
          options={chartTypeOptions}
          className="w-32"
        />
      </div>
      <Chart data={data} type={chartType as any} height={250} />
    </>
  );
};
