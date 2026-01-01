export async function GET(
  request: Request,
  { params }: { params: { studentId: string } }
) {
  try {
    const { studentId } = params
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'

    const response = await fetch(`${baseUrl}/api/student/${studentId}/progress`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error('Failed to fetch student progress')
    }

    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    console.error('Error fetching student progress:', error)
    return Response.json({ error: 'Failed to fetch student progress' }, { status: 500 })
  }
}
