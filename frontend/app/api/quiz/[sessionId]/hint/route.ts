export async function GET(
  request: Request,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params
    const { searchParams } = new URL(request.url)
    const questionId = searchParams.get('question_id')
    const hintIndex = searchParams.get('hint_index') || '0'
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'

    const response = await fetch(
      `${baseUrl}/api/quiz/${sessionId}/hint?question_id=${questionId}&hint_index=${hintIndex}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      throw new Error('Failed to fetch hint')
    }

    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    console.error('Error fetching hint:', error)
    return Response.json({ error: 'Failed to fetch hint' }, { status: 500 })
  }
}
