/**
 * 生产安全的日志工具
 *
 * 开发环境：输出到控制台
 * 生产环境：禁用日志或发送到监控系统
 */

const isDev = import.meta.env.DEV

class Logger {
  log(...args) {
    if (isDev) {
      console.log(...args)
    }
  }

  info(...args) {
    if (isDev) {
      console.info(...args)
    }
  }

  warn(...args) {
    if (isDev) {
      console.warn(...args)
    } else {
      // 生产环境发送到监控系统
      this.reportToMonitoring('warn', args)
    }
  }

  error(...args) {
    if (isDev) {
      console.error(...args)
    } else {
      // 生产环境发送到错误追踪系统（如 Sentry）
      this.reportToMonitoring('error', args)
    }
  }

  debug(...args) {
    if (isDev) {
      console.debug(...args)
    }
  }

  reportToMonitoring(level, args) {
    // TODO: 集成 Sentry 或其他监控服务
    // Example:
    // if (window.Sentry) {
    //   window.Sentry.captureMessage(args.join(' '), level)
    // }
  }
}

export default new Logger()
