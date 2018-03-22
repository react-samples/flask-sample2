from flask import Flask, request, render_template
import psycopg2
import psycopg2.extras

app = Flask(__name__)

conn = psycopg2.connect("dbname=testdb")
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

@app.route('/', methods=['GET'])
def index():
    cur.execute('SELECT * FROM messages')
    messages = cur.fetchall()
    messages = [ dict(message) for message in messages ]

    return render_template('index.html', messages=messages)

@app.route('/post', methods=['GET'])
def form():
    if request.method == 'GET':
        return render_template('form.html')

@app.route('/post', methods=['POST'])
def post():
    if request.method == 'POST':
         try:
             cur.execute("INSERT INTO messages (username, message) VALUES (%s, %s)", (request.form['username'], request.form['message']))
             conn.commit()

             return render_template('result.html', username=request.form['username'], message=request.form['message'])
         except Exception as e:
             return render_template('error.html')
