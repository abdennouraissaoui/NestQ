from flask_restful import Resource, reqparse
from models.user import UserModel
from models.portfolio import PortfolioModel
from blacklist import BLACKLIST
from werkzeug.security import (
    generate_password_hash,
    check_password_hash)
from flask_jwt_extended import (
    jwt_refresh_token_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt)
from datetime import timedelta
from misc.default_portfolios import DEFAULT_PORTFOLIOS
from finance.data_manager import get_colors

class UserRegister(Resource):
    user_parser = reqparse.RequestParser()
    user_parser.add_argument('email', type=str, required=True, help="You must provide an email")
    user_parser.add_argument('password', type=str, required=True, help="You must provide a password")
    user_parser.add_argument('firstName', type=str, required=True, help="You must provide a first name")
    user_parser.add_argument('lastName', type=str, required=True, help="You must provide a last name")

    @classmethod
    def post(cls):
        data = cls.user_parser.parse_args()
        if UserModel.find_by_email(data['email']):
            return {'message': 'This email address already exists'}, 400
        data['password'] = generate_password_hash(data['password'])
        new_user = UserModel(**data)  # data['email'], data['password'], user parser insures it only has 2
        new_user.save_to_db()
        # create the default portfolios for the user
        for portfolio_meta in DEFAULT_PORTFOLIOS:
            portfolio = PortfolioModel(portfolio_meta["name"], new_user.id, portfolio_meta)
            portfolio.save_to_db()

        access_token = create_access_token(identity=new_user.id, fresh=True, expires_delta=timedelta(hours=3))
        refresh_token = create_refresh_token(new_user.id)
        return {
                   'access_token': access_token,
                   'refresh_token': refresh_token,
               }, 200


class UserLogin(Resource):
    user_parser = reqparse.RequestParser()
    user_parser.add_argument('email', type=str, required=True, help="You must provide an email")
    user_parser.add_argument('password', type=str, required=True, help="You must provide a password")

    @classmethod
    def post(cls):
        data = cls.user_parser.parse_args()
        user = UserModel.find_by_email(data['email'])
        if user and check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True, expires_delta=timedelta(hours=3))
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
            }, 200
        return {'message': 'Invalid credentials'}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']  # jti is  JWT ID => unique identifier for jwt
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False, expires_delta=timedelta(hours=1))
        return {'access_token': new_token}, 200


class UserPortfolios(Resource):
    @jwt_required
    def get(self):
        user = UserModel.find_by_id(get_jwt_identity())
        user_portfolios = user.portfolios_json()
        max_num_holdings = 0
        for portfolio in user_portfolios["portfolios"]:
            num_holdings = len(portfolio["settings"]["holdings"])
            max_num_holdings = num_holdings if num_holdings > max_num_holdings else max_num_holdings
        user_portfolios["colors"] = get_colors(max_num_holdings)
        return user_portfolios

