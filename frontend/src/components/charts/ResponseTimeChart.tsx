import React from 'react';
import Chart, { ChartProps } from '../ui/Chart';

interface ResponseTimeChartProps {
  data: ChartProps['data'];
}

export const ResponseTimeChart: React.FC<ResponseTimeChartProps> = ({ data }) => {
  return <Chart data={data} type="bar" height={250} />;
};
