from app import create_app, db
from app.models import User, Post

app = create_app()



#Delete this if things get messy
app.run(ssl_context=('cert.pem', 'key.pem'), host="0.0.0.0", debug=True)
#app.run(host="0.0.0.0", debug=True)
#---------------------------------------------

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'FeedItem': FeedItem, 'Feeds': Feeds}
