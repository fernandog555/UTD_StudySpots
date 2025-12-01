// Review model
class Review {
  id: number
  spot_id: number
  author: string
  rating: number
  text: string
  date: string

  constructor(
    author = 'anonymous',
    text = '',
    rating = 5,
    date = new Date().toISOString().slice(0, 10), 
    spot_id = 0,
    id = 0
  ) {
    this.id = id
    this.spot_id = spot_id
    this.author = author
    this.rating = rating
    this.text = text
    this.date = date
  }
}

export type ReviewShape = {
  id?: number
  spot_id?: number
  author: string
  rating: number
  text: string
  date?: string
}

export default Review
