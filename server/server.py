from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys
sys.path.append(r'/home/ubuntu/server/calculatorLobachevsky')
sys.path.append(r'/home/ubuntu/server/calculator_methods')
from matrix import *
from expression import *
from combinatorics import *
from sympy import *

class ServerHandler(BaseHTTPRequestHandler):

    #logger
    def logs(self, request, response):
        print('Request: ' + request)
        print('Response: ' + response)

    #headers sender
    def send_basic_headers(self):
        self.send_header('Access-Control-Allow-Methods','POST, OPTIONS')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'origin, x-requested-with, content-type')

    #json request parser
    def parse_json(self):
        self.query_string = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        data = json.loads(self.query_string)
        return data

    #result sender
    def send_result(self, response):
        response = {'response' : response}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print('Request: ' + str(self.query_string))
        print('Response: ' + str(response))

    #error handlers
    def json_error_handler(self):
        self.send_response(400)
        self.send_basic_headers()
        self.end_headers()
        self.send_result('json.decoder.JSONDecodeError')

    def key_error_handler(self):
        self.send_response(400)
        self.send_basic_headers()
        self.end_headers()
        self.send_result('KeyError')

    def type_error_handler(self):
        self.send_response(400)
        self.send_basic_headers()
        self.end_headers()
        self.send_result('TypeError')

    def syntax_error_handler(self):
        self.send_response(400)
        self.send_basic_headers()
        self.end_headers()
        self.send_result('SyntaxError')


    #math handlers
    def expression_handler(self, data):
        obj = Expression(data)
        return(str(obj.calculate()))

    def matrix_handler(self, data):
        operation = data['operation']
        values = data['values']
        obj = Matrix(values)
        if operation == 'det':
            result = obj.det()
        elif operation == 'transposition':
            result = obj.transposition()
        elif operation == 'rank':
            result = obj.rank()
        elif operation == 'stepped':
            result = obj.stepped_view()
        return(str(result))

    def twomatrix_handler(self, data):
        operation = data['operation']
        values = data['values']
        obj1 = Matrix(values['matrix1'])
        obj2 = Matrix(values['matrix2'])
        if operation == '+':
            result = obj1 + obj2
        elif operation == '-':
            result = obj1 - obj2
        elif operation == '*':
            result = obj1 * obj2
        return(str(result))

    def equation_handler(self, data):
        return('equation')

    def inequality_handler(self, data):
        return('inequality')

    def derivative_handler(self, data):
        expr = data['expression']
        var = data['var']
        n = data['n']
        x = symbols(var)
        result = str(Derivative(expr, x, n).doit()).replace('**','^')
        return result

    def indef_integral_handler(self, data):
        expr = data['expression']
        var = data['var']
        x = symbols(var)
        result = str(Integral(expr, x).doit()).replace('**','^')
        return result

    def def_integral_handler(self, data):
        expr = data['expression']
        var = data['var']
        limits = data['limits']
        a = limits[0]
        b = limits[1]
        if a == 'inf' or a == '+inf':
            a = 'oo'
        elif a == '-inf':
            a = '-oo'
        if b == 'inf' or b == '+inf':
            b = 'oo'
        elif b == '-inf':
            b = '-oo'
        x = symbols(var)
        result = str(Integral(expr, (x, a, b)).doit()).replace('**','^')
        return result

    def combinatorics_handler(self, data):
        operation = data['operation']
        values = data['values']
        if operation == 'combinations':
            n = values[0]
            k = values[1]
            result = combinations(n, k)
            return result
        elif operation == 'repeat_combinations':
            n = values[0]
            k = values[1]
            result = repeat_combinations(n, k)
            return result
        elif operation == 'permutations':
            n = values[0]
            k = values[1]
            result = permutations(n, k)
            return result
        elif operation == 'repeat_permutations':
            n = values[0]
            k = values[1]
            result = repeat_permutations(n, k)
            return result
        elif operation == 'replacements':
            n = values[0]
            result = replacements(n)
            return result
        elif operation == 'repeat_replacements':
            n = values[0]
            k = values[1]
            result = repeat_replacements(n, k)
            return result

    def limit_handler(self, data):
        expr = data['expression']
        point = data['point']
        if point == 'inf' or point == '+inf':
            point = 'oo'
        elif point == '-inf':
            point = '-oo'
        var = data['var']
        x = symbols(var)
        result = str(limit(expr, x, point)).replace('**','^')
        return result

    def series_handler(self, data):
        expr = data['expression']
        result = str(series(expr)).replace('**','^')
        return result

    #request handlers
    def json_request_handler(self):
        try:
            self.request_json = self.parse_json()
            type = self.request_json['type']
            data = self.request_json['data']
            self.type_request_handler(type, data)
        except json.decoder.JSONDecodeError:
            self.json_error_handler()

    def type_request_handler(self, type, data):
        if type == 'expression':
            try:
                result = self.expression_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'matrix':
            try:
                result = self.matrix_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'twomatrix':
            try:
                result = self.twomatrix_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'sigma':
            try:
                result = self.sigma_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'equation':
            try:
                result = self.equation_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'inequality':
            try:
                result = self.inequality_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'derivative':
            try:
                result = self.derivative_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'point_derivative':
            try:
                result = self.point_derivative_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'indef_integral':
            try:
                result = self.indef_integral_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'def_integral':
            try:
                result = self.def_integral_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'combinatorics':
            try:
                result = self.combinatorics_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'limit':
            try:
                result = self.limit_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        elif type == 'series':
            try:
                result = self.series_handler(data)
                self.good_request()
                self.send_result(result)
            except KeyError:
                self.key_error_handler()
        else:
            self.key_error_handler()
    #response 200
    def good_request(self):
        self.send_response(200)
        self.send_basic_headers()
        self.end_headers()

    #POST handler
    def do_POST(self):
        if self.path == "/calculate":
            try:
                self.json_request_handler()
            except TypeError:
                self.type_error_handler()
            except:
                self.syntax_error_handler()
        else:
            self.send_error(406)

    #OPTIONS handler
    def do_OPTIONS(self):
        self.good_request()

    def do_GET(self):
        if self.path == '/types':
            content = "<html><body><h1 align='center'>!Vsem privet na etoi stranichke!</h1><p>types: expression, matrix, twomatrix, sigma, equation, inequality, derivative, point_derivative, indef_integral, def_integral, combinatorics, limit<br>Send JSON request to http://3.141.244.76/calculation {'type': <u>'type'</u>, 'data': <u>'any data'</u>}</p></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_error(404)



def server_thread(port):
    server_address = ('172.31.42.141', port)
    httpd = HTTPServer(server_address, ServerHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    port = 80
    print("Starting server at port %d" % port)
    server_thread(port)
