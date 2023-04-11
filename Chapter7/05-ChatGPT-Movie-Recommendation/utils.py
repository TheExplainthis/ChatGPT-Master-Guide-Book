import numpy as np
import datetime


def vector_similarity(x, y):
    return np.dot(np.array(x), np.array(y))


def query_similarity(query_embedding, contexts_embedding):
    document_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), int(doc_index)) for doc_index, doc_embedding in contexts_embedding.items()
    ], reverse=True)

    return document_similarities


def construct_sections(most_relevant_document_sections, db_results):
    chosen_sections = []
    MAX_SECTION_LEN = 1800
    for _, section_index in most_relevant_document_sections:
        movie = db_results[section_index]
        if len(chosen_sections) > MAX_SECTION_LEN:
            break

        txt = f"""
        index: {section_index}
        anticipation: {movie['anticipation']}
        type: {movie['type']}
        english_name: {movie['english_name']}
        anticipation: {movie['anticipation']}
        release_date: {movie['release_date']}
        length: {movie['length']}
        company: {movie['company']}
        imdb_rate: {movie.get('imdb_rate', None)}
        director: {movie['director']}
        cast: {movie['cast']}
        rated: {movie['rated']}
        story: {movie['story'][:100]}
        """
        chosen_sections.append(txt)
    return '\n'.join(chosen_sections)


def get_embedding_from_db(db):
    now = datetime.datetime.now()
    last_month_date = now - datetime.timedelta(days=30)
    movies = db['info'].find({
        'release_date': {
            '$gte': last_month_date.strftime('%Y-%m-%d')
        }
    })
    return list(movies)


def save_movie_info(movies, db, models, EMBEDDING_MODEL_ENGINE):
    for movie in movies:
        _ = movie.pop('movie_schedule_time', None)
        movie_details = movie['movie_detailed']
        release_info = movie['movie_detailed']['release_info']
        db['info'].update_one({
            'name': movie['movie_name']
        }, {
            '$set': {
                'name': movie['movie_name'],
                'website_url': movie['website_url'],
                'image_url': movie_details['image_url'],
                'type': movie_details['movie_type'],
                'english_name': movie['movie_english_name'],
                'anticipation': movie['anticipation'],
                'release_date': movie['release_time'],
                'length': release_info['movie_length'],
                'company': release_info['company'],
                'imdb_rate': release_info.get('imdb_rate', None),
                'director': release_info['director'],
                'cast': release_info['cast'],
                'rated': movie_details['rated'],
                'story': movie_details['story'],
                'embedding': models.embedding(str(movie), EMBEDDING_MODEL_ENGINE)
            }
        }, upsert=True)
        # save_schedule_time(movie, schedule_time, db)


def save_schedule_time(movie, schedule_time, db):
    for date, locations in schedule_time.items():
        for location, theaters in locations.items():
            for theater in theaters:
                for video_type, times in theater['movie_start_times'].items():
                    db['times'].update_one({
                        'date': date,
                        'name': movie['movie_name'],
                        'location': location,
                        'theater_name': theater['theater_name']
                    }, {
                        '$set': {
                            'date': date,
                            'name': movie['movie_name'],
                            'location': location,
                            'theater_name': theater['theater_name'],
                            'theater_phone': theater['theater_phone'],
                            'movie_start_times': {
                                video_type: times.split(', ')
                            }
                        }
                    }, upsert=True)
