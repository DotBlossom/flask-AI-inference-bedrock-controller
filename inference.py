from flask import Blueprint, request, jsonify



inference_bp = Blueprint('inference', __name__)

#private Callable Functions Set


@inference_bp.route('/ai-api/inference/result/<int:userId>', methods=['GET']) 
def get_inference_result(userId):
    
    return 'a'


@inference_bp.route('/ai-api/inference/<int:userId>', methods=['POST']) 
def inference_invoke(userId):

    return 'a'


@inference_bp.route('/ai-api/embed/product/<int:productId>', methods=['POST']) 
def product_embed_invoke(productId):

    return 'a'


@inference_bp.route('/ai-api/embed/user/<int:userId>', methods=['POST']) 
def user_embed_invoke(userId):

    return 'a'


