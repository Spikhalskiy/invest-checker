import vertx
from core.http import RouteMatcher

def get_accounts(req): req.response.end('You requested dogs')

server = vertx.create_http_server()

route_matcher = RouteMatcher()

route_matcher.get('/accounts', get_accounts)

server.request_handler(route_matcher).listen(8080, 'localhost')