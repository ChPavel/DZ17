# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')          # Регистрация неймспэйсов
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

class Movie(db.Model):              # Модель для фильмов.
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class MovieSchema(Schema):              # Схема для фильмов.
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Str()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):           # Модель для режиссёров.
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class DirectorSchema(Schema):       # Схема для режиссёров.
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):              # Модель для жанров.
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class GenreSchema(Schema):          # Схема для жанров.
    id = fields.Int()
    name = fields.Str()

                                    # Создание экземпляров схем для:
director_schema = DirectorSchema()              # одного;
directors_schema = DirectorSchema(many=True)    # многих;
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

@movie_ns.route('/')
class MoviesView(Resource):
    """
    Класс имеет метод возвращающий все фильмы либо фильмы по параметрам director_id и (или) genre_id.
    """
    def get(self):
        movies_query = db.session.query(Movie)
        args = request.args

        director_id = args.get('director_id')
        if director_id is not None:
            movies_query = movies_query.filter(Movie.director_id == director_id)

        genre_id = args.get('genre_id')
        if genre_id is not None:
            movies_query = movies_query.filter(Movie.genre_id == genre_id)

        movies = movies_query.all()
        return movies_schema.dump(movies), 200

@movie_ns.route('/<int:uid>/')
class MovieView(Resource):
    """
    Класс имеет метод, возвращающий фильм по id.
    """
    def get(self, uid: int):
        movie_1 = Movie.query.get(uid)
        if movie_1 is None:
            return {}, 404
        movie = movie_schema.dump(movie_1)
        return movie, 200

@director_ns.route('/')
class DirectorsView(Resource):
    """
    Класс имеет методs, возвращающий всех режиссёров и добавляющий режиссёра.
    """
    def get(self):
        directors_list = db.session.query(Director).all()
        directors = directors_schema.dump(directors_list)
        return directors, 200

    def post(self):
        req_json = request.json
        director = Director(**req_json)
        with db.session.begin():
            db.session.add(director)
        return "", 201


@director_ns.route('/<int:d_id>/')
class DirectorView(Resource):
    """
    Класс имеет методы, возвращающий, изменяющий, удаляющий режиссёра по id.
    """
    def get(self, d_id: int):
        director_1 = db.session.query(Director).filter(Director.id == d_id).one()
        if director_1 is None:
            return {}, 404
        director = director_schema.dump(director_1)
        return director, 200

    def put(self, d_id: int):
        director_1 = db.session.query(Director).filter(Director.id == d_id).one()
        if director_1 is None:
            return {}, 404
        req_json = request.json
        director_1.name = req_json.get("name")
        db.session.add(director_1)
        db.session.commit()
        return "", 204

    def delete(self, d_id: int):
        director_1 = db.session.query(Director).filter(Director.id == d_id).one()
        if director_1 is None:
            return {}, 404
        db.session.delete(director_1)
        db.session.commit()
        return "", 204


@genre_ns.route('/')
class GenresView(Resource):
    """
    Класс имеет метод, возвращающий все жанры и добавляющий жанр.
    """
    def get(self):
        genres_list = Genre.query.all()
        genres = genres_schema.dump(genres_list)
        return genres, 200

    def post(self):
        req_json = request.json
        genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(genre)
        return "", 201

@genre_ns.route('/<int:g_id>/')
class GenreView(Resource):
    """
    Класс имеет метод, возвращающий, изменяющий и удаляющий жанр по id.
    """
    def get(self, g_id: int):
        genre_1 = db.session.query(Genre).filter(Genre.id == g_id).one()
        if genre_1 is None:
            return {}, 404
        genre = genre_schema.dump(genre_1)
        return genre, 200

    def put(self, g_id: int):
        genre_1 = db.session.query(Genre).filter(Genre.id == g_id).one()
        if genre_1 is None:
            return {}, 404
        req_json = request.json
        genre_1.name = req_json.get("name")
        db.session.add(genre_1)
        db.session.commit()
        return "", 204

    def delete(self, g_id: int):
        genre_1 = db.session.query(Genre).filter(Genre.id == g_id).one()
        if genre_1 is None:
            return {}, 404
        db.session.delete(genre_1)
        db.session.commit()
        return "", 204

if __name__ == '__main__':
    app.run(debug=True)
