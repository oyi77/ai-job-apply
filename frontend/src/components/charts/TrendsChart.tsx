import React from 'react';
import Chart, { ChartProps } from '../ui/Chart';

interface TrendsChartProps {
  data: ChartProps['data'];
}

export const TrendsChart: React.FC<TrendsChartProps> = ({ data }) => {
  return <Chart data={data} type="line" height={250} />;
};
