'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, Suspense } from 'react';

/**
 * Inner component that uses useSearchParams
 */
function PracticeRedirectInner() {
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    const chapter = searchParams?.get('chapter');
    const gradeLevel = searchParams?.get('gradeLevel') || '6';
    
    if (chapter) {
      // Redirect to quiz with the same parameters
      router.push(`/quiz?chapter=${chapter}&gradeLevel=${gradeLevel}`);
    } else {
      // Default redirect to chapters page
      router.push('/chapters');
    }
  }, [searchParams, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="bg-white rounded-3xl p-8 shadow-lg max-w-sm">
        <div className="flex justify-center mb-4">
          <svg className="w-12 h-12 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </div>
        <p className="text-center text-gray-700 font-semibold">Redirecting to practice session...</p>
      </div>
    </div>
  );
}

/**
 * Redirect from /practice?chapter=X to /quiz?chapter=X
 * 
 * This maintains backward compatibility if anyone tries to access
 * the practice route directly.
 */
export default function PracticeRedirect() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white rounded-3xl p-8 shadow-lg max-w-sm">
          <div className="flex justify-center mb-4">
            <svg className="w-12 h-12 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
          <p className="text-center text-gray-700 font-semibold">Loading...</p>
        </div>
      </div>
    }>
      <PracticeRedirectInner />
    </Suspense>
  );
}
