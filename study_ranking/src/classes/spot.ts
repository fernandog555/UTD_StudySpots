export default class StudySpot {
  id: number
  name: string
  description: string
  building_code: string
  area_description: string
  seating_capacity: number
  power_outlets: boolean
  natural_light: boolean
  open_24_7: boolean
  is_active: boolean
  creator_id: number
  rating: number
  categories: string[]

  constructor(
    name = 'default',
    description = 'default',
    id = 0,
    creator_id = 0,
    rating = 0,
    building_code = '',
    area_description = '',
    seating_capacity = 0,
    power_outlets = false,
    natural_light = false,
    open_24_7 = false,
    is_active = true,
    categories?: string[]
  ) {
    this.id = id
    this.name = name
    this.description = description
    this.creator_id = creator_id
    this.rating = rating
    this.building_code = building_code
    this.area_description = area_description
    this.seating_capacity = seating_capacity
    this.power_outlets = power_outlets
    this.natural_light = natural_light
    this.open_24_7 = open_24_7
    this.is_active = is_active
    this.categories = categories ?? []
  }
}
