from flask import Flask, request
from flasgger import Swagger, swag_from
from nameko.standalone.rpc import ClusterRpcProxy

app = Flask(__name__)
Swagger(app)
CONFIG = {'AMQP_URI': "amqp://guest:guest@121.42.249.43:5672"}


@app.route('/compute', methods=['POST'])
@swag_from('compute.yml')
def compute():
    operation = request.json.get('operation')
    value = request.json.get('value')
    other = request.json.get('other')
    email = request.json.get('email')
    msg = "Please wait the calculation, you'll receive an email with results"
    subject = "API Notification"

    with ClusterRpcProxy(CONFIG) as rpc:
        rpc.mail.send.call_async((email,), subject, msg)
        result = rpc.compute.compute.call_async(operation, value, other, (email,))
        return msg, 200


if __name__ == '__main__':
    app.run(debug=True, host='121.42.249.43', port=8328)

