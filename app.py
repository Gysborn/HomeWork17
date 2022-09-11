# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)
movies_ns = api.namespace('movies')


class Movie(db.Model):
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


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre = fields.Pluck(GenreSchema, 'name')
    director = fields.Pluck(DirectorSchema, 'name')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)




@movies_ns.route('/')
class MovieView(Resource):
    def get(self):
        genre_id = request.args.get("genre_id")
        if genre_id:
            result = db.session.query(Movie).filter(Movie.genre_id == genre_id)
            movies_schema.dump(result)

        director_id = request.args.get("director_id")
        if director_id:
            result = db.session.query(Movie).filter(Movie.director_id == director_id)
            return movies_schema.dump(result)

        else:
            all_movie = Movie.query.all()
            if not all_movie:
                return 'Error', 404
            return movies_schema.dump(all_movie)

    def post(self):
        new_movie = request.json
        if not new_movie:
            return 'Error', 404
        movie = Movie(**new_movie)
        db.session.add(movie)
        db.session.commit()
        return "putin loh", 200

@movies_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        movie = Movie.query.get(uid)
        if movie:
            result = movie_schema.dump(movie)
            return jsonify(result['title'], result['description'])
        else:
            return 'Ничего не найдено', 404
    def put(self, uid):
        movie = Movie.query.get(uid)
        if not movie:
            return 'Error', 404
        upd_move = request.json
        [setattr(movie, k, v) for k, v in upd_move.items()]
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def patch(self, uid):
        movie = Movie.query.get(uid)
        if not movie:
            return 'Error', 404
        upd_move = request.json
        [setattr(movie, k, v) for k, v in upd_move.items()]
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, uid):
        movie = Movie.query.get(uid)
        if not movie:
            return 'Error', 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
