export async function GET(request: Request) {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'
    const response = await fetch(`${baseUrl}/api/categories`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error('Failed to fetch categories')
    }

    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    console.error('Error fetching categories:', error)
    return Response.json({ error: 'Failed to fetch categories' }, { status: 500 })
  }
}
