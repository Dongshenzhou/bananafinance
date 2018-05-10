from flask_mysqldb import MySQL
import my_database

def getIdolIdByUsername(username):
    followed_user = my_database.queryAll("SELECT follow.idol FROM follow JOIN users ON follow.follower = users.id WHERE users.username = %s", [username])
    return followed_user

def getIdolId(user_id):
    followed_user = my_database.queryAll("SELECT idol FROM follow WHERE follower = %s", [user_id])
    return followed_user

def getIdol(user_id):
    followed_user = my_database.queryAll("SELECT users.id, users.username, users.first_name, users.last_name FROM users JOIN follow ON users.id = follow.idol WHERE follow.follower = %s", [user_id])
    return followed_user

def getFollower(user_id):
    followed_by_user = my_database.queryAll("SELECT users.id, users.username, users.first_name, users.last_name FROM users JOIN follow ON users.id = follow.follower WHERE follow.idol = %s", [user_id])
    return followed_by_user

def follow(user_be_followed, follow_by_user):
    my_database.update("INSERT INTO follow(idol, follower) VALUES(%s, %s)", (user_be_followed, follow_by_user))

def unfollow(user_be_followed, follow_by_user):
    my_database.update("DELETE FROM follow where idol = %s and follower = %s", (user_be_followed, follow_by_user))
