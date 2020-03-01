# def configure_views(app):
#     @app.route('/<key>')
#     def get(key, db: SQLAlchemy):
#         try:
#             kv = db.session.query(KeyValue).filter(KeyValue.key == key).one()
#         except NoResultFound:
#             response = jsonify(status='No such key', context=key)
#             response.status = '404 Not Found'
#             return response
#         return jsonify(key=kv.key, value=kv.value)

    # @app.route('/')
    # def list(db: SQLAlchemy):
    #
    #     result = db.session.query(KeyValue).order_by(KeyValue.id)
    #     for item in result:
    #         print(item)
    #
    #     data = [i.code for i in db.session.query(KeyValue).order_by(KeyValue.id)]
    #     return jsonify(keys=data)
    #
    # @app.route('/index')
    # def index():
    #
    #     return render_template('index.html')


    # @app.route('/', methods=['POST'])
    # def create(request: Request, db: SQLAlchemy):
    #     kv = KeyValue(request.form['key'], request.form['value'])
    #     db.session.add(kv)
    #     db.session.commit()
    #     response = jsonify(status='OK')
    #     response.status = '201 CREATED'
    #     return response

    # @app.route('/<key>', methods=['DELETE'])
    # def delete(db: SQLAlchemy, key):
    #     db.session.query(KeyValue).filter(KeyValue.key == key).delete()
    #     db.session.commit()
    #     response = jsonify(status='OK')
    #     response.status = '200 OK'
    #     return response


# client = app.test_client()
#
# response = client.get('/')
# print('%s\n%s%s' % (response.status, response.headers, response.data))
# response = client.post('/', data={'key': 'foo', 'value': 'bar'})
# print('%s\n%s%s' % (response.status, response.headers, response.data))
# response = client.get('/')
# print('%s\n%s%s' % (response.status, response.headers, response.data))
# response = client.get('/hello')
# print('%s\n%s%s' % (response.status, response.headers, response.data))
# response = client.delete('/hello')
# print('%s\n%s%s' % (response.status, response.headers, response.data))
# response = client.get('/')
# print('%s\n%s%s' % (response.status, response.headers, response.data))
# response = client.get('/hello')
# print('%s\n%s%s' % (response.status, response.headers, response.data))
# response = client.delete('/hello')
# print('%s\n%s%s' % (response.status, response.headers, response.data))