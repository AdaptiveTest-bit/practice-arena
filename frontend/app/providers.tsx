'use client'

import React from 'react'
import { StudentProvider } from '@/lib/studentContext'

export function Providers({ children }: { children: React.ReactNode }) {
  return <StudentProvider>{children}</StudentProvider>
}
