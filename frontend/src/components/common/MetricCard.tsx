import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  icon: LucideIcon;
  variant?: 'blue' | 'emerald' | 'red' | 'purple';
  trend?: string;
  trendPositive?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'blue',
  trend,
  trendPositive = true
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'emerald':
        return {
          cardBg: 'bg-[#0b1b1e]/80 border-emerald-500/30 hover:border-emerald-500/50',
          iconBg: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40',
          valueColor: 'text-emerald-400',
          trendColor: 'text-emerald-400'
        };
      case 'red':
        return {
          cardBg: 'bg-[#201016]/80 border-red-500/30 hover:border-red-500/50',
          iconBg: 'bg-red-500/20 text-red-400 border border-red-500/40',
          valueColor: 'text-red-400',
          trendColor: 'text-red-400'
        };
      case 'purple':
        return {
          cardBg: 'bg-[#181024]/80 border-purple-500/30 hover:border-purple-500/50',
          iconBg: 'bg-purple-500/20 text-purple-400 border border-purple-500/40',
          valueColor: 'text-purple-300',
          trendColor: 'text-purple-400'
        };
      case 'blue':
      default:
        return {
          cardBg: 'bg-[#0d162a]/80 border-blue-500/30 hover:border-blue-500/50',
          iconBg: 'bg-blue-500/20 text-cyan-400 border border-blue-500/40',
          valueColor: 'text-cyan-300',
          trendColor: 'text-cyan-400'
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <div className={`p-4 rounded-xl backdrop-blur-md border transition-all duration-200 ${styles.cardBg}`}>
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <p className="text-[11px] font-semibold text-slate-400 tracking-wider uppercase font-sans">
            {title}
          </p>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-bold font-mono tracking-tight ${styles.valueColor}`}>
              {value}
            </span>
            {trend && (
              <span className={`text-xs font-medium ${styles.trendColor}`}>
                {trend}
              </span>
            )}
          </div>
          <p className="text-[11px] text-slate-400">{subtitle}</p>
        </div>

        <div className={`p-3 rounded-xl ${styles.iconBg} shadow-inner shrink-0`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
};
