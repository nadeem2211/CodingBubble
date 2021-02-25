from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class Restfultest(Resource):
    def get(self):
        return {'response' : "hello from get"}
    
    def post(self):
        some_json = request.get_json()
        return {'you sent':some_json}

class Multiply(Resource):
    def get(self,num):
        return {'result' : num*10 }

api.add_resource(Restfultest,'/')
api.add_resource(Multiply,'/<int:num>')

if __name__ == "__main__":
    app.run(debug=True)