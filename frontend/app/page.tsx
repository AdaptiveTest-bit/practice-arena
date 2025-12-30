import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Subtle animated background elements */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-blue-300/10 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '4s' }}></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-300/10 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '6s' }}></div>
      
      <div className="text-center relative z-10 max-w-3xl">
        {/* Main Title */}
        <div className="mb-8">
          <h1 className="text-5xl md:text-7xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 mb-4 leading-tight">
            Practice Arena
          </h1>
          <div className="h-1.5 w-40 bg-gradient-to-r from-blue-500 to-purple-500 mx-auto rounded-full"></div>
        </div>

        {/* Subtitle */}
        <div className="mb-12">
          <p className="text-xl md:text-3xl text-gray-700 font-semibold mb-2 leading-relaxed">
            Master Mathematics Through
          </p>
          <p className="text-xl md:text-3xl bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 font-black">
            Smart & Interactive Learning
          </p>
        </div>

        {/* Feature Points */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white/70 backdrop-blur-sm border border-gray-200 rounded-2xl p-6 hover:shadow-lg hover:border-blue-300 transition-all transform hover:scale-105">
            <span className="text-4xl mb-3 block">📚</span>
            <p className="text-gray-700 font-semibold">12 Chapters</p>
            <p className="text-sm text-gray-500 mt-1">All CBSE Topics</p>
          </div>
          <div className="bg-white/70 backdrop-blur-sm border border-gray-200 rounded-2xl p-6 hover:shadow-lg hover:border-blue-300 transition-all transform hover:scale-105">
            <span className="text-4xl mb-3 block">🎯</span>
            <p className="text-gray-700 font-semibold">Smart Questions</p>
            <p className="text-sm text-gray-500 mt-1">Adaptive Difficulty</p>
          </div>
          <div className="bg-white/70 backdrop-blur-sm border border-gray-200 rounded-2xl p-6 hover:shadow-lg hover:border-blue-300 transition-all transform hover:scale-105">
            <span className="text-4xl mb-3 block">⚡</span>
            <p className="text-gray-700 font-semibold">Instant Feedback</p>
            <p className="text-sm text-gray-500 mt-1">Learn & Improve</p>
          </div>
        </div>

        {/* CTA Button */}
        <Link
          href="/chapters"
          className="inline-block px-12 py-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-2xl font-bold text-lg hover:from-blue-600 hover:to-indigo-700 transition-all shadow-lg hover:shadow-2xl transform hover:scale-110 active:scale-95"
        >
          🚀 Start Practicing Now
        </Link>

        {/* Footer Text */}
        <p className="mt-12 text-gray-600 text-base font-medium">
          <span className="text-sm">✨</span> Begin your learning journey • Practice at your pace • Track your progress
        </p>

        {/* Testimonial */}
        <div className="mt-16 p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-gray-200 max-w-lg mx-auto">
          <p className="text-gray-700 font-semibold italic">
            "Learning math has never been this fun! 🎉"
          </p>
          <p className="text-sm text-gray-500 mt-2">— Grade 5 Student</p>
        </div>
      </div>
    </div>
  )
}
