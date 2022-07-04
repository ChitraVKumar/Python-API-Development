from audioop import cross
from gettext import find
from typing import Optional
from urllib import response
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

# Create instance of FastAPI
app = FastAPI()

# Create a class to represent what as post should look like
class Post(BaseModel):
    Title: str
    Content: str
    published: bool = True
    Rating: Optional[int] = None

# Creating a DB connection using psycopg2
while True:
    try:
        conn = psycopg2.connect(host= 'localhost', 
        database = 'Python API Development', user = 'postgres', password = 'root', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break

    except Exception as error:
        print("Connection to Database was failed!")
        print("Error: ", error)
        time.sleep(10)


# CReating a list to store all the posts
my_posts = [{"Title": "Title of post 1", "Content": "Content of post 1", "id": 1}, 
            {"Title": "Favorite Foods", "Content": "Biryani", "id": 2}]

# Finding a post from a list of posts
def find_post(id):
    for a_post in my_posts:
        if a_post['id'] == id:
            return a_post

# create a function to find index of the post for delete
def find_index_post(id):
    for i, a_post in enumerate(my_posts):
        if a_post['id'] == id:
            return i

# Path Operation for root page
@app.get("/")
async def root():
    return {"message": "Welcome to API.com"}

#path operation for posts page
@app.get("/posts")
def get_posts():
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall() 
    return {"data": posts}

# path operation for POST method
@app.post("/posts", status_code=status.HTTP_201_CREATED)    # changing the default status code for create post
def create_posts(post: Post): # create a variable called post and pass the class Post Pydamtic model as its value.
    # print(post.Title)
    # print(post.Content)
    # print(post.published)
    # print(post.Rating)
    # print(post)
    
    # To convert pydantic model into a dict
    # post_dict = post.dict()
    # # Reference the id to create unique id for every post
    # post_dict['id'] = randrange(0, 1000000)
    # # appending the dict with id to the list my_posts
    # my_posts.append(post_dict)
    cursor.execute("""INSERT INTO posts ("Title", "Content", published) VALUES (%s, %s, %s) RETURNING 
    * """, 
                    (post.Title, post.Content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

# Retrieve individual post
@app.get("/posts/{id}") # path parameter is the id field
def get_post(id: int, response: Response):  # validate the id type to int, create parameter response
    cursor.execute("""SELECT * from posts WHERE id = %s""", (str(id), ))
    post = cursor.fetchone()
    
    # post = find_post(id)   # convert the id value from str to int
    # If the post does not exist
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"Post with id: {id} NOT FOUND!")
        # Use raise to drop exceptopn instaed of hardcoding below
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"Post with id: {id} NOT FOUND!"}
    # print(post)
    return {"post_detail": post}

# path operation for delete
@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s returning * """, (str(id), ))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{id} does not exist!!")

    #return {'message': 'The post was deleted successfully!'} After deletion mo data is returned to the user except 204, do use below code instead
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Path operation to update posts with Put
@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET "Title" = %s, "Content" = %s, published = %s WHERE id = %s returning * """,
    (post.Title, post.Content, post.published, str(id), ))
    updated_post = cursor.fetchone()
    conn.commit()
    # index = find_index_post(id) # find the index of the post to upadte
    
    # If index not found
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{id} does not exist!!")
    
    # post_dict = post.dict()
    
    # post_dict['id'] = id
    
    # my_posts[index] = post_dict
    return {"data": updated_post}

# run the API using--> uvicorn main:app