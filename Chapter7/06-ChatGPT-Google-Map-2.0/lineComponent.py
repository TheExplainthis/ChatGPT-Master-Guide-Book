import os

TEXT_COLOR = '#666666'
LABEL_COLOR = '#aaaaaa'
PHOTO_URL = f"{os.getenv('SERVER_URL')}/image/"


class LineComponent():
    def __init__(self):
        pass

    def _rate_icon_component(self, rate, **kwargs):
        if rate < 0.125:
            url = 'https://explainthis.s3.ap-northeast-1.amazonaws.com/icons/review_0_star_28.png'
        elif rate < 0.375:
            url = 'https://explainthis.s3.ap-northeast-1.amazonaws.com/icons/review_0.25_star_28.png'
        elif rate < 0.625:
            url = 'https://explainthis.s3.ap-northeast-1.amazonaws.com/icons/review_0.5_star_28.png'
        elif rate < 0.875:
            url = 'https://explainthis.s3.ap-northeast-1.amazonaws.com/icons/review_0.75_star_28.png'
        else:
            url = 'https://explainthis.s3.ap-northeast-1.amazonaws.com/icons/review_1_star_28.png'
        return {
            'type': 'icon',
            'url': url,
            **kwargs
        }

    def _price_icon_component(self, type, **kwargs):

        if type == 'gray':
            url = 'https://explainthis.s3.ap-northeast-1.amazonaws.com/icons/money_gray_28.png'
        else:
            url = 'https://explainthis.s3.ap-northeast-1.amazonaws.com/icons/money_color_28.png'

        return {
            'type': 'icon',
            'url': url,
            **kwargs
        }

    def _text_component(self, **kwargs):
        return {
            'type': 'text',
            **kwargs
        }

    def _box_component(self, **kwargs):
        return {
            'type': 'box',
            **kwargs
        }

    def _uri_component(self, **kwargs):
        return {
            'type': 'uri',
            **kwargs
        }

    def _image_component(self, **kwargs):
        return {
            'type': 'image',
            **kwargs
        }

    def _button_component(self, url='', label=''):
        return {
            'type': 'button',
            'style': 'link',
            'height': 'sm',
            'action': {
                'type': 'uri',
                'label': label,
                'uri': url
            }
        }

    def _bubble_container(self, hero, body, footer):
        return {
            'type': 'bubble',
            'hero': hero,
            'body': body,
            'footer': footer
        }

    def _carousel_container(self, **kwargs):
        return {
            'type': 'carousel',
            **kwargs
        }

    def get_contents(self, places):
        contents = []
        for place in places:

            q = int(place['rating'])
            r = place['rating'] - q
            icons = [self._rate_icon_component(rate=1, size='sm')] * q + [self._rate_icon_component(rate=r, size='sm')]

            price_level = place.get('price_level', 0)
            price_icons = [self._price_icon_component(type='color', size='sm')] * price_level + [self._price_icon_component(type='gray', size='sm')] * (4-price_level)

            comment = '無評論'
            if place.get('reviews', []) != []:
                comment = place.get('reviews', [])[0]['text'][:50]
            hero = self._image_component(url=f"{PHOTO_URL}{place['photo_name']}", size='full', aspectMode='cover', aspectRatio='10:12')

            body = self._box_component(layout='vertical', contents=[
                self._text_component(text=place['name'], weight='bold', size='xl'),
                self._box_component(layout='baseline', contents=[
                    *icons,
                    self._text_component(text=str(place.get('rating', 0)), color=TEXT_COLOR, size='sm', margin='md', flex=0)
                ]),
                self._box_component(layout='baseline', contents=[
                    *price_icons
                ]),
                self._box_component(layout='vertical', contents=[
                    self._box_component(layout='baseline', contents=[
                        self._text_component(text='地址', color=LABEL_COLOR, size='sm', flex=2),
                        self._text_component(text=place.get('address', '無'), color=TEXT_COLOR, size='sm', wrap=True, flex=5)
                    ]),
                    self._box_component(layout='baseline', contents=[
                        self._text_component(text='評論數', color=LABEL_COLOR, size='sm', flex=2),
                        self._text_component(text=f"{str(place.get('user_ratings_total', 0))} 則", color=TEXT_COLOR, size='sm', wrap=True, flex=5)
                    ]),
                    self._box_component(layout='baseline', contents=[
                        self._text_component(text='評論', color=LABEL_COLOR, size='sm', flex=2),
                        self._text_component(text=comment, color=TEXT_COLOR, size='sm', wrap=True, flex=5)
                    ]),
                ])
            ])
            footer = self._box_component(layout='vertical', spacing='sm', contents=[
                self._button_component(url=place.get('url', 'https://www.google.com.tw/maps'), label='Google Map')
            ])
            contents.append(self._bubble_container(hero=hero, body=body, footer=footer))
        return self._carousel_container(contents=contents)


line_component = LineComponent()
