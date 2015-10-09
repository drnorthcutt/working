#
# Database access functions for the web forum.
#

import time
import psycopg2
import bleach


# Database connection
def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=forum")


# Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    # Re-clean code, just in case.
    DB = connect()
    c = DB.cursor()
    c.execute('''

                SELECT time, content
                    FROM posts
                    ORDER BY time DESC;

              ''')
    posts = [{'content': str(bleach.clean(row[1])), 'time': str(row[0])}
             for row in c.fetchall()]
    DB.close()
    return posts


# Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
    sparkling = bleach.clean(content)  # Prevent SQL injection
    DB = connect()
    c = DB.cursor()
    # Stop quotes passing as code
    c.execute('''

                INSERT INTO posts
                           (content)
                    VALUES (%s);

              ''', (sparkling,))
    DB.commit()
    DB.close()
