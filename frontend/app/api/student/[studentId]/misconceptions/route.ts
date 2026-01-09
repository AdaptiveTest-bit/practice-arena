export async function GET(
  request: Request,
  { params }: { params: Promise<{ studentId: string }> }
) {
  try {
    const { studentId } = await params
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'

    const response = await fetch(
      `${baseUrl}/api/student/${studentId}/misconceptions`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      throw new Error('Failed to fetch misconceptions')
    }

    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    console.error('Error fetching misconceptions:', error)
    return Response.json({ error: 'Failed to fetch misconceptions' }, { status: 500 })
  }
}
