/**
 * ECharts 工具函数
 * 解决 echarts.graphic.LinearGradient 在某些版本中的兼容性问题
 */

/**
 * 创建线性渐变色对象（兼容所有 ECharts 版本）
 * 使用对象语法替代 new echarts.graphic.LinearGradient
 */
export function createLinearGradient(x, y1, x2, y2, colorStops) {
  return {
    type: 'linear',
    x: x,
    y: y1,
    x2: x2,
    y2: y2,
    colorStops: colorStops
  }
}

/**
 * 创建径向渐变色对象
 */
export function createRadialGradient(x, y, r, colorStops) {
  return {
    type: 'radial',
    x: x,
    y: y,
    r: r,
    colorStops: colorStops
  }
}
