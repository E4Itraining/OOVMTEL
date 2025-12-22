import React from 'react'
import { motion } from 'framer-motion'

export function RadialGauge({ value, max = 100, size = 128, strokeWidth = 10, label, color = 'cyan' }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const progress = Math.min(value / max, 1)
  const offset = circumference - progress * circumference

  const colorMap = {
    cyan: { stroke: '#06b6d4', shadow: 'rgba(6, 182, 212, 0.3)' },
    green: { stroke: '#22c55e', shadow: 'rgba(34, 197, 94, 0.3)' },
    yellow: { stroke: '#f59e0b', shadow: 'rgba(245, 158, 11, 0.3)' },
    red: { stroke: '#ef4444', shadow: 'rgba(239, 68, 68, 0.3)' },
    purple: { stroke: '#a855f7', shadow: 'rgba(168, 85, 247, 0.3)' },
  }

  const getColorByValue = () => {
    if (value >= 85) return colorMap.green
    if (value >= 70) return colorMap.cyan
    if (value >= 50) return colorMap.yellow
    return colorMap.red
  }

  // Handle hex colors directly if not in colorMap
  const getActiveColor = () => {
    if (color === 'auto') return getColorByValue()
    if (colorMap[color]) return colorMap[color]
    // If color is a hex value or not in colorMap, create a color object from it
    return { stroke: color, shadow: `${color}4D` } // 4D is ~30% opacity in hex
  }

  const activeColor = getActiveColor()

  return (
    <div className="relative inline-flex flex-col items-center justify-center">
      <svg
        width={size}
        height={size}
        className="-rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(51, 65, 85, 0.5)"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={activeColor.stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{
            filter: `drop-shadow(0 0 8px ${activeColor.shadow})`
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className="text-3xl font-bold text-white"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          {Math.round(value)}
        </motion.span>
        <span className="text-xs text-gray-400">{label || '%'}</span>
      </div>
    </div>
  )
}

export function SemiCircleGauge({ value, max = 100, label, subLabel, size = 200 }) {
  const progress = Math.min(value / max, 1)
  const angle = progress * 180

  const getColor = () => {
    if (value >= 85) return '#22c55e'
    if (value >= 70) return '#06b6d4'
    if (value >= 50) return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className="relative" style={{ width: size, height: size / 2 + 40 }}>
      <svg
        width={size}
        height={size / 2 + 20}
        viewBox={`0 0 ${size} ${size / 2 + 20}`}
      >
        {/* Background arc */}
        <path
          d={`M 20 ${size / 2} A ${size / 2 - 20} ${size / 2 - 20} 0 0 1 ${size - 20} ${size / 2}`}
          fill="none"
          stroke="rgba(51, 65, 85, 0.5)"
          strokeWidth="16"
          strokeLinecap="round"
        />
        {/* Progress arc */}
        <motion.path
          d={`M 20 ${size / 2} A ${size / 2 - 20} ${size / 2 - 20} 0 0 1 ${size - 20} ${size / 2}`}
          fill="none"
          stroke={getColor()}
          strokeWidth="16"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: progress }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          style={{
            filter: `drop-shadow(0 0 10px ${getColor()}40)`
          }}
        />
      </svg>
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center">
        <motion.div
          className="text-4xl font-bold text-white"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {Math.round(value)}%
        </motion.div>
        {label && <div className="text-sm text-gray-400 mt-1">{label}</div>}
        {subLabel && <div className="text-xs text-gray-500">{subLabel}</div>}
      </div>
    </div>
  )
}

export function LinearGauge({ value, max = 100, label, showValue = true, color = 'cyan', height = 'h-2' }) {
  const progress = Math.min((value / max) * 100, 100)

  const colorMap = {
    cyan: 'bg-cyan-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500',
    gradient: 'bg-gradient-to-r from-cyan-500 to-purple-500',
  }

  const getColorByValue = () => {
    if (value >= 80) return 'bg-green-500'
    if (value >= 60) return 'bg-cyan-500'
    if (value >= 40) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const barColor = color === 'auto' ? getColorByValue() : colorMap[color]

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex justify-between items-center mb-1">
          {label && <span className="text-sm text-gray-400">{label}</span>}
          {showValue && <span className="text-sm font-medium text-white">{Math.round(value)}%</span>}
        </div>
      )}
      <div className={`progress-bar ${height}`}>
        <motion.div
          className={`progress-bar-fill ${barColor}`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

export function MultiGauge({ segments, size = 160 }) {
  const radius = (size - 20) / 2
  const circumference = 2 * Math.PI * radius
  let cumulativeOffset = 0

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        {/* Background */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(51, 65, 85, 0.3)"
          strokeWidth="12"
        />
        {/* Segments */}
        {segments.map((segment, i) => {
          const segmentLength = (segment.value / 100) * circumference
          const offset = circumference - cumulativeOffset - segmentLength
          cumulativeOffset += segmentLength

          return (
            <motion.circle
              key={i}
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke={segment.color}
              strokeWidth="12"
              strokeDasharray={`${segmentLength} ${circumference}`}
              strokeDashoffset={-cumulativeOffset + segmentLength}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.2, duration: 0.5 }}
            />
          )
        })}
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {segments.map((segment, i) => (
          <div key={i} className="flex items-center gap-1 text-xs">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: segment.color }} />
            <span className="text-gray-400">{segment.label}: {segment.value}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
