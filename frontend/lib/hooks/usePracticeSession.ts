/**
 * Hook for managing practice session state
 */

import { useContext } from 'react'
import { PracticeContext } from '@/lib/context/PracticeContext'
import { PracticeContextType } from '@/lib/types'

export function usePracticeSession(): PracticeContextType {
  const context = useContext(PracticeContext)
  
  if (!context) {
    throw new Error('usePracticeSession must be used within PracticeProvider')
  }
  
  return context as PracticeContextType
}
