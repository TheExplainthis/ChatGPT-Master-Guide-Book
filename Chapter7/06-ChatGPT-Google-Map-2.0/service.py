import requests
import uuid
import urllib


class GoogleMap():
    def __init__(self, api_token):
        self.api_token = api_token
        self.BASE_URL = 'http://maps.google.com/maps?q={}'

    def get_places(self, keyword):
        url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={keyword}&key={self.api_token}&language=zh-TW'
        r = requests.get(url).json()
        res = []
        for place in r['results']:
            photo_name = f'{str(uuid.uuid4())}.png'
            photo_reference = ''
            if place.get('photos'):
                photo_reference = place['photos'][0]['photo_reference']
                self.get_photo_from_reference(f'photos/{photo_name}', photo_reference)

            res.append({
                'name': place.get('name'),
                'place_id': place.get('place_id'),
                'business_status': place.get('business_status', ''),
                'open_now': place.get('opening_hours', {}).get('open_now', False),
                'address': place.get('formatted_address', ''),
                'lat': place.get('geometry', {}).get('location', {}).get('lat', ''),
                'lon': place.get('geometry', {}).get('location', {}).get('lng', ''),
                'price_level': place.get('price_level', 0),
                'rating': place.get('rating', 0),
                'url': self.BASE_URL.format(urllib.parse.quote(place.get('name', ''))),
                'photo_name': photo_name,
                'types': ','.join(place.get('types', [])),
                'photo_reference': photo_reference,
                'user_ratings_total': place.get('user_ratings_total', 0)
            })
        return res

    def get_details(self, place_id):
        fields = ','.join(['wheelchair_accessible_entrance', 'curbside_pickup', 'delivery', 'dine_in', 'editorial_summary', 'rating', 'reservable', 'reviews', 'serves_beer', 'serves_breakfast', 'serves_brunch', 'serves_dinner', 'serves_lunch', 'serves_vegetarian_food', 'serves_wine', 'takeout'])
        url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&key={self.api_token}&language=zh-TW'
        result = requests.get(url).json()['result']
        delivery = result.get('delivery')
        dine_in = result.get('dine_in')
        summary = result.get('editorial_summary', {}).get('overview')
        reservable = result.get('reservable')
        reviews = result.get('reviews')
        serves_beer = result.get('serves_beer', False)
        serves_breakfast = result.get('serves_breakfast', False)
        serves_brunch = result.get('serves_brunch', False)
        serves_dinner = result.get('serves_dinner', False)
        serves_lunch = result.get('serves_lunch', False)
        serves_wine = result.get('serves_wine', False)
        serves_vegetarian_food = result.get('serves_vegetarian_food', False)
        takeout = result.get('takeout', False)
        wheelchair_accessible_entrance = result.get('wheelchair_accessible_entrance', False)

        return {
            'delivery': delivery,
            'dine_in': dine_in,
            'summary': summary,
            'reservable': reservable,
            'reviews': reviews,
            'serves_beer': serves_beer,
            'serves_breakfast': serves_breakfast,
            'serves_brunch': serves_brunch,
            'serves_dinner': serves_dinner,
            'serves_lunch': serves_lunch,
            'serves_wine': serves_wine,
            'serves_vegetarian_food': serves_vegetarian_food,
            'takeout': takeout,
            'wheelchair_accessible_entrance': wheelchair_accessible_entrance,
        }

    def get_photo_from_reference(self, image_path, photo_reference):
        try:
            r = requests.get(f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={self.api_token}')
            with open(image_path, 'wb') as f:
                f.write(r.content)
            return True
        except Exception:
            return False
