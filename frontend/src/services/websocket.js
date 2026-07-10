/**
 * WebSocket 服务
 *
 * 提供实时通知功能
 */

class WebSocketService {
  constructor() {
    this.ws = null
    this.userId = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 3000
    this.listeners = new Map()
    this.isConnecting = false
  }

  /**
   * 连接WebSocket
   * @param {string} userId - 用户ID
   * @param {string} token - 认证Token（可选）
   */
  connect(userId, token = null) {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      console.log('WebSocket already connected or connecting')
      return
    }

    this.userId = userId
    this.isConnecting = true

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    const port = import.meta.env.VITE_WS_PORT || '8000'

    let url = `${protocol}//${host}:${port}/api/ws?user_id=${userId}`
    if (token) {
      url += `&token=${token}`
    }

    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        console.log('✓ WebSocket connected')
        this.isConnecting = false
        this.reconnectAttempts = 0
        this.emit('connected', { userId })
      }

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          console.log('WebSocket message:', message)
          this.handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.isConnecting = false
        this.emit('error', error)
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.isConnecting = false
        this.emit('disconnected')
        this.attemptReconnect()
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      this.isConnecting = false
    }
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.reconnectAttempts = this.maxReconnectAttempts // 防止自动重连
  }

  /**
   * 尝试重连
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnect attempts reached')
      this.emit('reconnect_failed')
      return
    }

    this.reconnectAttempts++
    console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      if (this.userId) {
        this.connect(this.userId)
      }
    }, this.reconnectInterval * this.reconnectAttempts)
  }

  /**
   * 发送消息
   * @param {object} message - 消息对象
   */
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected')
    }
  }

  /**
   * 订阅房间
   * @param {string} room - 房间名（dashboard, reviews, audits）
   */
  subscribe(room) {
    this.send({
      type: 'subscribe',
      room: room
    })
  }

  /**
   * 取消订阅房间
   * @param {string} room - 房间名
   */
  unsubscribe(room) {
    this.send({
      type: 'unsubscribe',
      room: room
    })
  }

  /**
   * 处理接收的消息
   * @param {object} message - 消息对象
   */
  handleMessage(message) {
    const { type } = message

    // 触发对应类型的监听器
    this.emit(type, message)

    // 特定类型处理
    switch (type) {
      case 'review_assigned':
        this.showNotification('新的审核任务', message.data?.transaction_id)
        break
      case 'review_completed':
        this.showNotification('审核已完成', message.data?.transaction_id)
        break
      case 'audit_completed':
        this.showNotification('审计已完成', message.data?.transaction_id)
        break
      case 'system_alert':
        this.showNotification(message.message, null, message.severity)
        break
      case 'heartbeat':
        // 响应心跳
        this.send({ type: 'ping' })
        break
    }
  }

  /**
   * 显示浏览器通知
   * @param {string} title - 标题
   * @param {string} body - 内容
   * @param {string} severity - 严重程度
   */
  showNotification(title, body, severity = 'info') {
    // 检查通知权限
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body: body,
        icon: '/favicon.ico',
        badge: '/favicon.ico'
      })
    }

    // 触发应用内通知事件
    this.emit('notification', { title, body, severity })
  }

  /**
   * 注册事件监听器
   * @param {string} event - 事件名
   * @param {function} callback - 回调函数
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  /**
   * 移除事件监听器
   * @param {string} event - 事件名
   * @param {function} callback - 回调函数
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  /**
   * 触发事件
   * @param {string} event - 事件名
   * @param {any} data - 事件数据
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in ${event} listener:`, error)
        }
      })
    }
  }

  /**
   * 请求通知权限
   */
  async requestNotificationPermission() {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      return permission === 'granted'
    }
    return false
  }

  /**
   * 获取连接状态
   */
  get isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

// 导出单例
export const wsService = new WebSocketService()

export default wsService
