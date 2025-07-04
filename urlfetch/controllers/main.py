from odoo import http
from odoo.http import Response

class UrlfetchController(http.Controller):
    @http.route('/urlfetch/ping', type='http', auth='public', methods=['GET'], csrf=False)
    def urlfetch_ping(self, **kwargs):
        return Response("OK", status=200, mimetype='text/plain')
