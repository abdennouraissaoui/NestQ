from models.portfolio import PortfolioModel
from finance.analytics import create_portfolio_tearsheet, create_comparison_tearsheet
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback


class PortfolioAnalytics(Resource):
    # TODO: add analysis period
    @jwt_required
    def post(self, portfolio_name):
        data_parser = reqparse.RequestParser()
        data_parser.add_argument("end")
        data_parser.add_argument("start")
        data = data_parser.parse_args()
        start = data['start'][:10] if data["start"] else None
        end = data['end'][:10] if data["end"] else None
        portfolio = PortfolioModel.find_by_name(portfolio_name, get_jwt_identity())
        if portfolio:
            try:
                return create_portfolio_tearsheet(portfolio, start, end), 200
            except Exception as e:
                traceback.print_exc()
                # return {"message": e}, 500
                return {"message": "Oops, an error occurred on our end"}, 500
        else:
            return {"message": "Portfolio by the name {} was not found".format(portfolio_name)}, 404


class PortfolioComparison(Resource):
    @jwt_required
    def post(self):
        data_parser = reqparse.RequestParser()
        data_parser.add_argument('compPortfolios',
                                 action='append',
                                 required=True,
                                 help="You must provide a list of portfolios")
        data_parser.add_argument("end")
        data_parser.add_argument("start")
        data = data_parser.parse_args()

        start = data['start'][:10] if data["start"] else None
        end = data['end'][:10] if data["end"] else None
        portfolios = []
        for portfolio_name in data['compPortfolios']:
            portfolio = PortfolioModel.find_by_name(portfolio_name, get_jwt_identity())
            if not portfolio:
                return {"message": "Portfolio by the name {} was not found".format(portfolio_name)}, 404
            else:
                portfolios.append(portfolio)
        try:
            return create_comparison_tearsheet(portfolios, start, end)
        except Exception as e:
            traceback.print_exc()
            return {"message": "Oops, an error occurred on our end"}, 500
