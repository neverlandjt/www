from src.rest_api.rest_api import app, cluster

app.config['JSON_AS_ASCII'] = False


if __name__ == '__main__':
    app.run(debug=True)
    cluster.shutdown()

