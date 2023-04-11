TEXT_COLOR = '#666666'
LABEL_COLOR = '#aaaaaa'


class LineComponent():
    def __init__(self):
        pass

    def _icon_component(self, type, **kwargs):
        if type == 'gold':
            url = 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'
        elif type == 'gray':
            url = 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png'
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

    def get_contents(self, movies):
        contents = []
        for movie in movies:
            imdb_rate = movie.get('imdb_rate', '') or 0
            imdb_rate = int(float(imdb_rate))
            movie_image_url = movie.get('image_url', '') or 'https://upload.wikimedia.org/wikipedia/commons/5/59/Empty.png?20091205084734'
            movie_name = movie.get('name', '') or '無'
            movie_type = ', '.join(movie.get('type', [])) or '無'
            movie_length = movie.get('length', '') or '無'
            movie_director = movie.get('director', '') or '無'
            movie_cast = movie.get('cast', '') or '無'
            movie_website = movie.get('website_url', '') or 'https://movies.yahoo.com.tw/movie_intheaters.html'

            icons = [self._icon_component(type='gold', size='sm')] * imdb_rate + [self._icon_component(type='gray', size='sm')] * (10 - imdb_rate)
            hero = self._image_component(url=movie_image_url, size='full', aspectMode='cover', aspectRatio='10:12')
            body = self._box_component(layout='vertical', contents=[
                self._text_component(text=movie_name, weight='bold', size='xl'),
                self._box_component(layout='baseline', contents=[
                    *icons,
                    self._text_component(text=str(movie.get('imdb_rate', '無')), color=TEXT_COLOR, size='sm', margin='md', flex=0)
                ]),
                self._box_component(layout='vertical', contents=[
                    self._box_component(layout='baseline', contents=[
                        self._text_component(text='類型', color=LABEL_COLOR, size='sm', flex=1),
                        self._text_component(text=movie_type, color=TEXT_COLOR, size='sm', wrap=True, flex=5)
                    ]),
                    self._box_component(layout='baseline', contents=[
                        self._text_component(text='片長', color=LABEL_COLOR, size='sm', flex=1),
                        self._text_component(text=movie_length, color=TEXT_COLOR, size='sm', wrap=True, flex=5)
                    ]),
                    self._box_component(layout='baseline', contents=[
                        self._text_component(text='導演', color=LABEL_COLOR, size='sm', flex=1),
                        self._text_component(text=movie_director, color=TEXT_COLOR, size='sm', wrap=True, flex=5)
                    ]),
                    self._box_component(layout='baseline', contents=[
                        self._text_component(text='演員', color=LABEL_COLOR, size='sm', flex=1),
                        self._text_component(text=movie_cast, color=TEXT_COLOR, size='sm', wrap=True, flex=5)
                    ])
                ])
            ])
            footer = self._box_component(layout='vertical', spacing='sm', contents=[
                self._button_component(url=movie_website, label='Website')
            ])
            contents.append(self._bubble_container(hero=hero, body=body, footer=footer))
        return self._carousel_container(contents=contents)


line_component = LineComponent()
