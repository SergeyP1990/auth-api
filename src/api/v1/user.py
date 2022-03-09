from flask import Blueprint, request, Response

user_register = Blueprint("user_register", __name__, url_prefix="/user")


@user_register.route("/register", methods=["POST"])
def register():
    print("REGUSTER_CALL")
    if request.method == 'POST':
        print("REQUEST IS POST")
        request_data = request.get_json()

        username = request_data['username']
        password = request_data['password']

        return Response("{'a':'b'}", status=200, mimetype="application/json")
