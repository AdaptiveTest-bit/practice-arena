import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface CoverageData {
  concept_coverage: Array<{
    concept_id: string
    concept_name: string
    total_questions: number
    published_questions: number
    coverage_percentage: number
    difficulty_distribution: {
      easy: number
      medium: number
      hard: number
      expert: number
    }
  }>
  bloom_coverage: Array<{
    level: string
    count: number
    percentage: number
  }>
  overall_stats: {
    total_concepts: number
    total_questions: number
    published_questions: number
    average_coverage: number
  }
}

async function fetchCoverageData(): Promise<CoverageData> {
  // Mock data - replace with actual API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        concept_coverage: [
          {
            concept_id: 'factors_multiples.find_factors',
            concept_name: 'Find Factors',
            total_questions: 50,
            published_questions: 40,
            coverage_percentage: 80,
            difficulty_distribution: {
              easy: 15,
              medium: 20,
              hard: 10,
              expert: 5
            }
          },
          {
            concept_id: 'factors_multiples.find_multiples',
            concept_name: 'Find Multiples',
            total_questions: 45,
            published_questions: 35,
            coverage_percentage: 78,
            difficulty_distribution: {
              easy: 10,
              medium: 20,
              hard: 10,
              expert: 5
            }
          },
          {
            concept_id: 'factors_multiples.gcd',
            concept_name: 'GCD Problems',
            total_questions: 30,
            published_questions: 20,
            coverage_percentage: 67,
            difficulty_distribution: {
              easy: 5,
              medium: 10,
              hard: 10,
              expert: 5
            }
          },
          {
            concept_id: 'factors_multiples.lcm',
            concept_name: 'LCM Problems',
            total_questions: 25,
            published_questions: 15,
            coverage_percentage: 60,
            difficulty_distribution: {
              easy: 5,
              medium: 8,
              hard: 7,
              expert: 5
            }
          },
          {
            concept_id: 'factors_multiples.divisibility',
            concept_name: 'Divisibility Tests',
            total_questions: 20,
            published_questions: 10,
            coverage_percentage: 50,
            difficulty_distribution: {
              easy: 8,
              medium: 7,
              hard: 3,
              expert: 2
            }
          }
        ],
        bloom_coverage: [
          { level: 'Remember', count: 20, percentage: 15 },
          { level: 'Understand', count: 40, percentage: 30 },
          { level: 'Apply', count: 35, percentage: 26 },
          { level: 'Analyze', count: 25, percentage: 19 },
          { level: 'Evaluate', count: 10, percentage: 7 },
          { level: 'Create', count: 5, percentage: 3 }
        ],
        overall_stats: {
          total_concepts: 5,
          total_questions: 170,
          published_questions: 120,
          average_coverage: 67
        }
      })
    }, 1000)
  })
}

export function CoverageDashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['coverage-data'],
    queryFn: fetchCoverageData,
  })

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-96 bg-gray-200 rounded"></div>
            <div className="h-96 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-danger-50 border border-danger-200 rounded-md p-4">
          <p className="text-danger-800">Error loading coverage data</p>
        </div>
      </div>
    )
  }

  const getCoverageColor = (percentage: number) => {
    if (percentage >= 80) return 'text-success-600'
    if (percentage >= 60) return 'text-warning-600'
    return 'text-danger-600'
  }

  const getCoverageBadge = (percentage: number) => {
    if (percentage >= 80) return 'badge-success'
    if (percentage >= 60) return 'badge-warning'
    return 'badge-danger'
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Coverage Dashboard</h1>
        <p className="text-gray-600">Overview of concept coverage and question distribution</p>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-primary-100">
              <div className="text-2xl font-bold text-primary-600">
                {data?.overall_stats.total_concepts}
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Concepts</p>
              <p className="text-xs text-gray-500">Across all chapters</p>
            </div>
          </div>
        </div>
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-primary-100">
              <div className="text-2xl font-bold text-primary-600">
                {data?.overall_stats.total_questions}
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Questions</p>
              <p className="text-xs text-gray-500">All templates</p>
            </div>
          </div>
        </div>
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-success-100">
              <div className="text-2xl font-bold text-success-600">
                {data?.overall_stats.published_questions}
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Published</p>
              <p className="text-xs text-gray-500">Live questions</p>
            </div>
          </div>
        </div>
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-warning-100">
              <div className="text-2xl font-bold text-warning-600">
                {data?.overall_stats.average_coverage}%
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Coverage</p>
              <p className="text-xs text-gray-500">Per concept</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Concept Coverage Chart */}
        <div className="card">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Concept Coverage</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data?.concept_coverage}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="concept_name" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="coverage_percentage" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bloom's Taxonomy Distribution */}
        <div className="card">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Bloom's Taxonomy Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data?.bloom_coverage}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ level, percentage }) => `${level} (${percentage}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {data?.bloom_coverage.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed Concept Coverage */}
      <div className="card">
        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Detailed Concept Coverage</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Concept
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Coverage
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Questions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Published
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Difficulty Distribution
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data?.concept_coverage.map((concept) => (
                  <tr key={concept.concept_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {concept.concept_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {concept.concept_id}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-1 mr-2">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                concept.coverage_percentage >= 80
                                  ? 'bg-success-500'
                                  : concept.coverage_percentage >= 60
                                  ? 'bg-warning-500'
                                  : 'bg-danger-500'
                              }`}
                              style={{ width: `${concept.coverage_percentage}%` }}
                            ></div>
                          </div>
                        </div>
                        <span className={`text-sm font-medium ${getCoverageColor(concept.coverage_percentage)}`}>
                          {concept.coverage_percentage}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {concept.total_questions}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {concept.published_questions}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex space-x-2 text-xs">
                        <div className="text-center">
                          <div className="font-medium text-gray-900">{concept.difficulty_distribution.easy}</div>
                          <div className="text-gray-500">Easy</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-900">{concept.difficulty_distribution.medium}</div>
                          <div className="text-gray-500">Med</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-900">{concept.difficulty_distribution.hard}</div>
                          <div className="text-gray-500">Hard</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-900">{concept.difficulty_distribution.expert}</div>
                          <div className="text-gray-500">Expert</div>
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Coverage Recommendations */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Coverage Recommendations</h2>
            <div className="space-y-3">
              {data?.concept_coverage
                .filter(concept => concept.coverage_percentage < 80)
                .map((concept) => (
                  <div key={concept.concept_id} className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-warning-500 rounded-full mt-2"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{concept.concept_name}</p>
                      <p className="text-xs text-gray-500">
                        Add {Math.ceil((80 - concept.coverage_percentage) / 100 * concept.total_questions)} more questions to reach 80% coverage
                      </p>
                    </div>
                  </div>
                ))}
              {data?.concept_coverage.every(concept => concept.coverage_percentage >= 80) && (
                <p className="text-sm text-gray-500">All concepts have good coverage!</p>
              )}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Difficulty Balance</h2>
            <div className="space-y-3">
              {data?.concept_coverage.map((concept) => {
                const total = Object.values(concept.difficulty_distribution).reduce((a, b) => a + b, 0)
                const hasBalance = concept.difficulty_distribution.easy >= 5 && 
                                  concept.difficulty_distribution.medium >= 5 && 
                                  concept.difficulty_distribution.hard >= 3
                
                return (
                  <div key={concept.concept_id} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">{concept.concept_name}</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      hasBalance ? 'bg-success-100 text-success-800' : 'bg-warning-100 text-warning-800'
                    }`}>
                      {hasBalance ? 'Balanced' : 'Needs Balance'}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
