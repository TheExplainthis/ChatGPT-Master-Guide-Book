def construct_sections(places):
    chosen_sections = []
    MAX_SECTION_LEN = 1800
    for place in places:
        if len("\n".join(chosen_sections)) > MAX_SECTION_LEN:
            break
        reviews = []
        if place.get('reviews'):
            for i, review in enumerate(place['reviews']):
                review_text = f"user_id: {i}, reviews_rating: {review['rating']}, reviews_text: {review['text'][:50]}"
                reviews.append(review_text)
        reviews = '\n'.join(reviews)
        txt = f"""
        name: {place.get('name')}
        place_id: {place.get('place_id')}
        business_status: {place.get('business_status')}
        open_now: {place.get('opening_hours', {}).get('open_now', False)}
        price_level: {place.get('price_level', -1)}
        rating: {place.get('rating')}
        types: {place.get('types')}
        user_ratings_total: {place.get('user_ratings_total')}
        delivery: {place.get('delivery')}
        dine_in: {place.get('dine_in')}
        summary: {place.get('summary')}
        reservable: {place.get('reservable')}
        reviews: {reviews}
        serves_beer: {place.get('serves_beer')}
        serves_breakfast: {place.get('serves_breakfast')}
        serves_brunch: {place.get('serves_brunch')}
        serves_dinner: {place.get('serves_dinner')}
        serves_lunch: {place.get('serves_lunch')}
        serves_wine: {place.get('serves_wine')}
        serves_vegetarian_food: {place.get('serves_vegetarian_food')}
        takeout: {place.get('takeout')}
        wheelchair_accessible_entrance: {place.get('wheelchair_accessible_entrance')}
        """
        chosen_sections.append(txt)
    return '\n'.join(chosen_sections)
