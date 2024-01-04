from webserver import HttpServer, render_template

server = HttpServer()


@server.route("/")
def index():
    return render_template("index.html")


@server.route("/test")
def index():
    return render_template("/test/test.html")


@server.route("/param-test")
def test(query_params):
    # the client needs to handle query parameters
    return str(query_params)


server.start()
