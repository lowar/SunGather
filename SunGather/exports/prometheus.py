import logging

from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from version import __version__

class export_prometheus(object):
    def __init__(self):
        self.metrics = ""

    def configure(self, config, inverter):
        # start web server
        try:
            self.web_server = HTTPServer(('', config.get('port',8080)), MyServer)
            self.t = Thread(target=self.web_server.serve_forever)
            self.t.daemon = True    # Make it a deamon, so if main loop ends the webserver dies
            self.t.start()
            logging.info(f"Webserver: Configured")
        except Exception as err:
            logging.error(f"Webserver: Error: {err}")
            return False
        return True

    def publish(self, inverter):
        res = ""
        for register, value in inverter.latest_scrape.items():
            try:
                float_value = float(str(value))
                res += "# HELP " + str(register) + " " + str(register) + " (" + str(inverter.getRegisterUnit(register)) + ")\n"
                res += "# TYPE " + str(register) + " gauge\n"
                res += str(register) + " " + str(float_value) + "\n"
            except ValueError:
                pass
        export_prometheus.metrics = res
        return True

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/metrics"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            self.wfile.write(bytes(export_prometheus.metrics, "utf-8"))
        elif self.path.startswith("/health"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("OK".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write("Not found".encode("utf-8"))

    def log_message(self, format, *args):
        pass
# vim: set tabstop=4 softtabstop=4 shiftwidth=4 expandtab autoindent smartindent syntax=python:
