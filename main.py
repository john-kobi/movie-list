from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
import requests


the_movie_db_api_key = '5ffa7248710b575494ce4442ab295466'
# example_request = "https://api.themoviedb.org/3/movie/550?api_key=5ffa7248710b575494ce4442ab295466"
access_token = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1ZmZhNzI0ODcxMGI1NzU0OTRjZTQ0NDJhYjI5NTQ2NiIsInN1YiI6IjYzYzJhMmZhMjNiZTQ2MDA4MTdkMTcyMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.03kBaulbSfLB2Nq0hHZn5PVxKL9smUADp2HUhUi30Fg'
movie_db_endpoint = 'https://api.themoviedb.org/3/search/movie?'
direct_query_endpoint = 'https://api.themoviedb.org/3/movie/?'
movie_image_base_url = 'https://image.tmdb.org/t/p/w500/'

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
all_movies = []

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

with app.app_context():
    class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(250), unique=True, nullable=False)
        year = db.Column(db.String(250), nullable=False)
        description = db.Column(db.String(250), nullable=False)
        rating = db.Column(db.String(250), nullable=False)
        ranking = db.Column(db.String(250), nullable=False)
        review = db.Column(db.String(250), unique=False, nullable=False)
        img_url = db.Column(db.String(250), unique=False, nullable=False)
        # director = db.Column(db.String(250), unique=False, nullable=False)

        def __repr__(self):
            return f'<Movie {self.title}>'

    db.create_all()
    db.session.commit()

    class FindMovieForm(FlaskForm):
        movie_title = StringField('Enter a title', validators=[DataRequired()])
        submit = SubmitField('Go!')

    class MovieForm(FlaskForm):
        title = StringField('Title', validators=[DataRequired()])
        year = StringField('Year', validators=[DataRequired()])
        description = StringField('Description', validators=[DataRequired()])
        rating = StringField('Rating from 0.0 - 10.0', validators=[DataRequired()])
        ranking = HiddenField('Ranking', validators=[DataRequired()])
        review = StringField('Review', validators=[DataRequired()])
        img_url = StringField('Image url', validators=[DataRequired()])
        # director = StringField('Director', validators=[DataRequired()])
        submit = SubmitField('Done')


    class MovieSearchForm(FlaskForm):
        search_movies = StringField('Search the top 100', validators=[DataRequired()])
        submit = SubmitField('Search')


@app.route('/', methods=["GET", "POST"])
def home():
    movie_search_form = MovieSearchForm()
    title_to_search = ''
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
        if request.method == "POST":
            title_to_search = request.form['search_movies']
            if title_to_search in all_movies[i].title.lower():
                print(all_movies[i].title)
                search_result = all_movies[i]
                return render_template('search.html', movie_search_form=movie_search_form, search_result=search_result)
    return render_template('index.html', movies=all_movies, movie_search_form=movie_search_form)


@app.route("/select", methods=["GET", "POST"])
def select():
    movie_api_id = request.args.get("id")
    print(movie_api_id)
    movie_url = f'https://api.themoviedb.org/3/movie/{movie_api_id}?api_key={the_movie_db_api_key}'
    if movie_api_id:
        response = requests.get(movie_url)
        data = response.json()
        print(data)
        print(data['title'])
        print(data["release_date"].split("-")[0])
        print(data['overview'])
        print(f"{movie_image_base_url}{data['poster_path']}")
        new_movie = Movie(
                # director=data['director'],
                title=data['title'],
                year=data["release_date"].split("-")[0],
                description=data['overview'],
                img_url=f"{movie_image_base_url}{data['poster_path']}",
                rating=0,
                ranking=0,
                review='',
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    err_msg = "There was an error, please try a different title."
    movie_form = FindMovieForm()
    if request.method == "POST":
        movie_title_query = request.form['movie_title']
        print(movie_title_query)
        response = requests.get(url=movie_db_endpoint, params={
            'api_key': the_movie_db_api_key,
            'query': movie_title_query,
        })
        data = response.json()['results']
        print(f"DATA: {data}")
        return render_template("select.html", options=data)

        # db.session.add(new_movie)
        # db.session.commit()

    return render_template('add.html', form=movie_form, err_msg=err_msg)


@app.route('/edit', methods=["GET", "POST"])
def edit():

    movies_db = Movie.query.all()
    movie_form = MovieForm()
    movie_id = request.args.get('id')
    movie_selected = Movie.query.get(movie_id)
    print(movie_selected.rating)
    if request.method == "POST":
        movie_to_update = Movie.query.get(movie_id)
        print(movie_to_update)
        if request.form["title"] != "":
            movie_to_update.title = request.form["title"]
        if request.form["year"] != "":
            movie_to_update.year = request.form["year"]
        if request.form["description"] != "":
            movie_to_update.description = request.form["description"]
        if request.form["rating"] != "":
            movie_to_update.rating = request.form["rating"]
        if request.form["ranking"] != "":
            movie_to_update.ranking = request.form["ranking"]
        if request.form["review"] != "":
            movie_to_update.review = request.form["review"]
        if request.form["img_url"] != "":
            movie_to_update.img_url = request.form["img_url"]
        # if request.form["cancel"]:
        #     return redirect(url_for('home'))
        db.session.commit()
        print(Movie)
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie_selected, form=movie_form)


@app.route('/delete', methods=["GET", "POST"])
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete_all')
def delete_all():
    movie_db_id = db.session.query(Movie.id).all()
    for item in movie_db_id:
        print(item)
        movie_to_delete = Movie.query.get(item)
        db.session.delete(movie_to_delete)
        db.session.commit()
    message = "All records deleted"
    return redirect(url_for('home', message=message))


if __name__ == "__main__":
    app.run(debug=True)
