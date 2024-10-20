from flask import Flask, render_template, request,jsonify
import pickle
import numpy as np
from colorama import Fore, Style


popular_df = pickle.load(open("popular.pkl", "rb"))
pt = pickle.load(open("pt.pkl", "rb"))
books = pickle.load(open("books.pkl", "rb"))
similarity_scores = pickle.load(open("similarity_scores.pkl", "rb"))

app = Flask(__name__)

@app.route("/")
def index():
    return render_template(
        "index.html",
        book_name=list(popular_df["Book-Title"].values),
        author=list(popular_df["Book-Author"].values),
        image=list(popular_df["Image-URL-M"].values),
        votes=list(popular_df["num_ratings"].values),
        rating=list(popular_df["avg_rating"].values),
    )


@app.route("/recommend")
def recommend_ui():
    return render_template("recommend.html")


@app.route("/recommend_books", methods=["post"])
def recommend():
    req = request.get_json()
    user_input = req['book_title']
    print(Fore.CYAN + user_input + Style.RESET_ALL) #validating if input is recieved
    datadf = books[books['Book-Title'] == user_input]
    populardf = popular_df[popular_df["Book-Title"] == user_input]
    info = {
        "Title":    datadf['Book-Title'].iloc[0],
        "Year" : datadf['Year-Of-Publication'].iloc[0],
        "Author" : datadf['Book-Author'].iloc[0],
        "image" : datadf['Image-URL-L'].iloc[0],
        "votes": populardf['num_ratings'].values[0] if populardf['num_ratings'].size >0 else "No Votes",
        "rating": populardf['avg_rating'].values[0] if populardf['avg_rating'].size >0 else "No Ratings"
    }
    print(info)
    indexdf = np.where(pt.index == user_input) 
    index = indexdf[0][0] if np.size(indexdf) > 0 else 0 
    similar_items = sorted(
        list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True
    )[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books["Book-Title"] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates("Book-Title")["Book-Title"].values))
        item.extend(list(temp_df.drop_duplicates("Book-Title")["Book-Author"].values))
        item.extend(list(temp_df.drop_duplicates("Book-Title")["Image-URL-M"].values))

        data.append(item)

    print(data)
    render = render_template("description.html", details = info, data=data)
    return jsonify({'html': render})


if __name__ == "__main__":
    app.run(debug=True)
