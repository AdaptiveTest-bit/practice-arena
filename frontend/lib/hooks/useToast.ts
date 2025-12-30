/**
 * Hook for toast notifications using react-hot-toast
 */

import toast from 'react-hot-toast'

interface ToastOptions {
  title: string
  description?: string
  type?: 'success' | 'error' | 'info' | 'loading'
  duration?: number
}

export function useToast() {
  const showToast = (options: ToastOptions) => {
    const { title, description, type = 'info', duration = 4000 } = options
    const message = description ? `${title}\n${description}` : title

    switch (type) {
      case 'success':
        toast.success(message, { duration })
        break
      case 'error':
        toast.error(message, { duration })
        break
      case 'loading':
        toast.loading(message, { duration: Infinity })
        break
      case 'info':
      default:
        toast(message, { duration })
    }
  }

  return { toast: showToast }
}
