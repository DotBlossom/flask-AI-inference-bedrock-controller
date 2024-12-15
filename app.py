from flask import Flask
from flask_cors import CORS

from result import result_bp, default_result_bp
from user_actions import user_actions_bp
from inference import inference_bp
from data_resolver import data_resolver_bp
from flow_controller import flow_controller_bp

# APP name definition
app = Flask(__name__)

# CORS Allowed All Origins
CORS(app)


#app.router

## return Prefernece ids to User table
app.register_blueprint(result_bp)
app.register_blueprint(default_result_bp)
## get user - product id in user Actions
app.register_blueprint(user_actions_bp)
## invoke inference
app.register_blueprint(inference_bp)

##
app.register_blueprint(data_resolver_bp)
app.register_blueprint(flow_controller_bp)
#EOL

# ECS HealthChecker Router
@app.route('/')
def home():
    
    return 'healthy'


# allowed all , container port : 5050
if __name__ == '__main__':  
   app.run('0.0.0.0',port=5050,debug=True)