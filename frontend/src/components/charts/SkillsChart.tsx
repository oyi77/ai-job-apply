import React from 'react';
import Chart, { ChartProps } from '../ui/Chart';

interface SkillsChartProps {
  data: ChartProps['data'];
}

export const SkillsChart: React.FC<SkillsChartProps> = ({ data }) => {
  return <Chart data={data} type="doughnut" height={250} />;
};
