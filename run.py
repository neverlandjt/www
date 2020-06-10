from src.rest_api.rest_api import app, cluster

app.config['JSON_AS_ASCII'] = False


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4321, debug=True)
    cluster.shutdown()
