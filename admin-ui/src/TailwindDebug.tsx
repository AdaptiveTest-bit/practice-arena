import React from 'react'

export default function TailwindDebug() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-blue-600 mb-4">Tailwind Debug Test</h1>
      <div className="bg-gray-100 p-4 rounded-lg mb-4">
        <p className="text-gray-800">If you see this styled, Tailwind is working!</p>
      </div>
      <div className="p-4 bg-green-100 border border-green-300 rounded">
        <p className="text-green-800">✅ This should be green with border if Tailwind CSS is loaded</p>
      </div>
      <div className="mt-4 p-4 bg-red-100 border border-red-300 rounded">
        <p className="text-red-800">❌ This should be red with border if Tailwind CSS is loaded</p>
      </div>
      <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
        Test Button
      </button>
    </div>
  )
}
