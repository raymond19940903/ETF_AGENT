import React, { useEffect, useRef, useState } from 'react';
import styles from './PieChart.module.css';

interface PieChartData {
  label: string;
  value: number;
  color?: string;
}

interface PieChartProps {
  data: PieChartData[];
  width?: number;
  height?: number;
  showLabels?: boolean;
  showLegend?: boolean;
  showTooltip?: boolean;
  animationDuration?: number;
}

/**
 * 自研饼图组件 - 科技风格设计
 * 使用Canvas绘制，支持渐变色彩和交互动画
 */
const PieChart: React.FC<PieChartProps> = ({
  data,
  width = 300,
  height = 300,
  showLabels = true,
  showLegend = true,
  showTooltip = true,
  animationDuration = 1000,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number>(-1);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; data: PieChartData } | null>(null);

  // 默认科技风配色
  const defaultColors = [
    '#1890FF', '#52C41A', '#FAAD14', '#FF4D4F', '#722ED1',
    '#13C2C2', '#EB2F96', '#F5222D', '#FA8C16', '#A0D911'
  ];

  // 为数据添加颜色
  const processedData = data.map((item, index) => ({
    ...item,
    color: item.color || defaultColors[index % defaultColors.length]
  }));

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 设置画布尺寸
    canvas.width = width;
    canvas.height = height;

    // 清空画布
    ctx.clearRect(0, 0, width, height);

    // 计算总值
    const total = processedData.reduce((sum, item) => sum + item.value, 0);
    if (total === 0) return;

    // 绘制饼图
    drawPieChart(ctx, processedData, total, width, height);

  }, [processedData, width, height, hoveredIndex]);

  const drawPieChart = (
    ctx: CanvasRenderingContext2D,
    data: PieChartData[],
    total: number,
    canvasWidth: number,
    canvasHeight: number
  ) => {
    const centerX = canvasWidth / 2;
    const centerY = canvasHeight / 2;
    const radius = Math.min(canvasWidth, canvasHeight) / 2 - 30;

    let startAngle = -Math.PI / 2;

    data.forEach((item, index) => {
      const sliceAngle = (item.value / total) * 2 * Math.PI;
      const isHovered = index === hoveredIndex;
      const currentRadius = isHovered ? radius + 8 : radius;

      // 绘制扇形
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, currentRadius, startAngle, startAngle + sliceAngle);
      ctx.closePath();

      // 创建渐变效果
      const gradient = ctx.createRadialGradient(
        centerX, centerY, 0,
        centerX, centerY, currentRadius
      );
      gradient.addColorStop(0, item.color!);
      gradient.addColorStop(1, adjustBrightness(item.color!, -20));

      ctx.fillStyle = gradient;
      ctx.fill();

      // 绘制边框
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      // 添加发光效果（悬停时）
      if (isHovered) {
        ctx.shadowColor = item.color!;
        ctx.shadowBlur = 10;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // 绘制标签
      if (showLabels && item.value / total > 0.05) {
        const labelAngle = startAngle + sliceAngle / 2;
        const labelRadius = currentRadius * 0.7;
        const labelX = centerX + Math.cos(labelAngle) * labelRadius;
        const labelY = centerY + Math.sin(labelAngle) * labelRadius;

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // 添加文字阴影
        ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
        ctx.shadowBlur = 2;
        ctx.fillText(`${((item.value / total) * 100).toFixed(1)}%`, labelX, labelY);
        ctx.shadowBlur = 0;
      }

      startAngle += sliceAngle;
    });
  };

  const handleMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!showTooltip) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // 计算鼠标位置对应的扇形
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 30;

    const distance = Math.sqrt((x - centerX) ** 2 + (y - centerY) ** 2);
    
    if (distance <= radius) {
      const angle = Math.atan2(y - centerY, x - centerX);
      const normalizedAngle = (angle + Math.PI / 2 + 2 * Math.PI) % (2 * Math.PI);
      
      const total = processedData.reduce((sum, item) => sum + item.value, 0);
      let currentAngle = 0;
      
      for (let i = 0; i < processedData.length; i++) {
        const sliceAngle = (processedData[i].value / total) * 2 * Math.PI;
        
        if (normalizedAngle >= currentAngle && normalizedAngle <= currentAngle + sliceAngle) {
          setHoveredIndex(i);
          setTooltip({
            x: event.clientX,
            y: event.clientY,
            data: processedData[i]
          });
          return;
        }
        
        currentAngle += sliceAngle;
      }
    }
    
    setHoveredIndex(-1);
    setTooltip(null);
  };

  const handleMouseLeave = () => {
    setHoveredIndex(-1);
    setTooltip(null);
  };

  // 调整颜色亮度
  const adjustBrightness = (color: string, amount: number): string => {
    const hex = color.replace('#', '');
    const r = Math.max(0, Math.min(255, parseInt(hex.substr(0, 2), 16) + amount));
    const g = Math.max(0, Math.min(255, parseInt(hex.substr(2, 2), 16) + amount));
    const b = Math.max(0, Math.min(255, parseInt(hex.substr(4, 2), 16) + amount));
    
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  };

  return (
    <div className={styles.pieChartContainer}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className={styles.canvas}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      />
      
      {showLegend && (
        <div className={styles.legend}>
          {processedData.map((item, index) => (
            <div 
              key={index} 
              className={classNames(styles.legendItem, {
                [styles.legendItemHovered]: index === hoveredIndex
              })}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(-1)}
            >
              <div
                className={styles.legendColor}
                style={{ backgroundColor: item.color }}
              />
              <span className={styles.legendLabel}>{item.label}</span>
              <span className={styles.legendValue}>
                {((item.value / processedData.reduce((sum, d) => sum + d.value, 0)) * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      )}
      
      {tooltip && (
        <div 
          className={styles.tooltip}
          style={{
            left: tooltip.x + 10,
            top: tooltip.y - 10,
          }}
        >
          <div className={styles.tooltipTitle}>{tooltip.data.label}</div>
          <div className={styles.tooltipValue}>
            数值: {tooltip.data.value.toFixed(2)}
          </div>
          <div className={styles.tooltipPercentage}>
            占比: {((tooltip.data.value / processedData.reduce((sum, d) => sum + d.value, 0)) * 100).toFixed(1)}%
          </div>
        </div>
      )}
    </div>
  );
};

export default PieChart;
