'use client'
import React from 'react'
import Link from 'next/link'

const CHAPTERS = [
	{
		id: 'large_numbers',
		name: '🔢 Large Numbers',
		description: 'The Fish Tale - Place value and big numbers',
		color: 'from-blue-400 to-blue-500',
	},
	{
		id: 'clock_angles',
		name: '⏰ Clock Angles',
		description: 'Shapes & Angles - Time and angles',
		color: 'from-red-400 to-red-500',
	},
	{
		id: 'symmetry',
		name: '🪞 Symmetry',
		description: 'Shapes & Angles - Lines of symmetry',
		color: 'from-indigo-400 to-indigo-500',
	},
	{
		id: 'rotation',
		name: '🔄 Rotation',
		description: 'Shapes & Angles - Geometric transformations',
		color: 'from-cyan-400 to-cyan-500',
	},
	{
		id: 'fraction_area',
		name: '📐 Fractions in Area',
		description: 'How Many Squares - Fractions using area',
		color: 'from-green-400 to-green-500',
	},
	{
		id: 'fractions_decimals',
		name: '🍰 Fractions & Decimals',
		description: 'Parts & Wholes - Conversions and operations',
		color: 'from-yellow-400 to-yellow-500',
	},
	{
		id: 'dice_logic',
		name: '🎲 Dice Logic',
		description: 'Does it Look the Same - 3D visualization',
		color: 'from-purple-400 to-purple-500',
	},
	{
		id: 'nets',
		name: '📦 Nets & Solids',
		description: 'Does it Look the Same - 3D shapes and nets',
		color: 'from-orange-400 to-orange-500',
	},
	{
		id: 'factors_multiples',
		name: '🎯 Factors & Multiples',
		description: 'Be My Multiple - HCF, LCM, divisibility',
		color: 'from-teal-400 to-teal-500',
	},
	{
		id: 'data_patterns',
		name: '🔍 Data Patterns',
		description: 'Can You See Pattern - Sequences and rules',
		color: 'from-fuchsia-400 to-fuchsia-500',
	},
	{
		id: 'mapping',
		name: '🗺️ Mapping',
		description: 'Mapping Your Way - Coordinates and scales',
		color: 'from-rose-400 to-rose-500',
	},
	{
		id: 'cube_counting',
		name: '🧩 Cube Counting',
		description: 'Boxes & Sketches - 3D spatial reasoning',
		color: 'from-pink-400 to-pink-500',
	},
	{
		id: 'geometry_measurement',
		name: '📏 Area & Measurement',
		description: 'Geometry & Measurement - Area, perimeter, volume',
		color: 'from-lime-400 to-lime-500',
	},
	{
		id: 'data_handling',
		name: '📈 Data Handling',
		description: 'Smart Charts - Graphs and statistics',
		color: 'from-green-400 to-green-500',
	},
	{
		id: 'multiplication_division',
		name: '✖️ Multiplication & Division',
		description: 'Ways to Multiply/Divide - Strategies and properties',
		color: 'from-amber-400 to-amber-500',
	},
	{
		id: 'measurement',
		name: '⚖️ Measurement',
		description: 'How Big/Heavy - Units, weight, capacity',
		color: 'from-violet-400 to-violet-500',
	},
]

export default function ChaptersPage() {
	return (
		<div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 md:py-16 md:px-6 relative overflow-hidden">
			{/* Subtle animated background elements */}
			<div
				className="absolute top-0 right-0 w-96 h-96 bg-blue-300/5 rounded-full blur-3xl animate-pulse"
				style={{ animationDuration: '4s' }}
			></div>
			<div
				className="absolute bottom-0 left-0 w-96 h-96 bg-purple-300/5 rounded-full blur-3xl animate-pulse"
				style={{ animationDuration: '6s' }}
			></div>

			<div className="max-w-7xl mx-auto relative z-10">
				{/* Header */}
				<div className="text-center mb-16">
					<div className="mb-6">
						<h1 className="text-4xl md:text-6xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 mb-4">
							Choose Your Chapter
						</h1>
					</div>
					<p className="text-lg text-gray-700 mb-8 max-w-2xl mx-auto font-semibold">
						Select a topic and master mathematical concepts through smart,
						interactive learning
					</p>
					<Link
						href="/"
						className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-bold text-sm transition hover:bg-blue-50 px-4 py-2 rounded-lg"
					>
						← Back to Home
					</Link>
				</div>

				{/* Chapter Grid */}
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
					{CHAPTERS.map((chapter) => (
						<Link key={chapter.id} href={`/practice?chapter=${chapter.id}`} className="group">
							<div className="relative h-full">
								{/* Card with gradient border */}
								<div
									className={`relative bg-gradient-to-br ${chapter.color} rounded-3xl p-1 h-full shadow-lg group-hover:shadow-2xl transition-all duration-300 transform group-hover:scale-105`}
								>
									{/* Inner white card */}
									<div className="bg-white rounded-3xl p-8 h-full flex flex-col justify-between">
										{/* Content */}
										<div>
											{/* Icon + Title */}
											<h3 className="text-3xl font-black text-gray-900 mb-4 leading-snug">
												{chapter.name}
											</h3>

											{/* Description */}
											<p className="text-gray-600 mb-6 leading-relaxed font-semibold">
												{chapter.description}
											</p>
										</div>

										{/* CTA Button */}
										<div className="inline-flex items-center gap-3 text-sm font-bold text-white px-5 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 group-hover:from-blue-600 group-hover:to-indigo-600 transition-all transform group-hover:scale-110 shadow-md">
											<span>Start</span>
											<svg
												className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													strokeLinecap="round"
													strokeLinejoin="round"
													strokeWidth={3}
													d="M9 5l7 7-7 7"
												/>
											</svg>
										</div>
									</div>
								</div>
							</div>
						</Link>
					))}
				</div>

				{/* Footer Stats */}
				<div className="text-center pt-8 border-t border-gray-300">
					<p className="text-gray-700 text-sm font-semibold">
						<span className="text-blue-600 text-lg font-black">
							{CHAPTERS.length} Chapters
						</span>{' '}
						• Comprehensive CBSE Mathematics Curriculum
					</p>
				</div>
			</div>
		</div>
	)
}
