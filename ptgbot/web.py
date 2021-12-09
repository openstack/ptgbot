import argparse
import daemon
import daemon.pidfile
import http.server
import json
import logging
import os
import pkg_resources
import socketserver

CONFIG = {}


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('ptg.json'):
            with open(CONFIG['db_filename'], 'rb') as fp:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(fp.read())
        else:
            http.server.SimpleHTTPRequestHandler.do_GET(self)

    def log_message(self, format, *args):
        logging.debug("%s - - [%s] %s" % (self.address_string(),
                                          self.log_date_time_string(),
                                          format % args))


def start():
    os.chdir(CONFIG['source_dir'])
    with socketserver.TCPServer(("", CONFIG['port']), RequestHandler) as httpd:
        httpd.serve_forever()


def main():
    global CONFIG
    parser = argparse.ArgumentParser(description='PTG web')
    parser.add_argument('configfile', help='config file')
    parser.add_argument('-d', dest='nodaemon', action='store_true',
                        help='do not run as daemon')
    parser.add_argument('-p', '--port', dest='port', help='Port to listen on',
                        default=8000)
    parser.add_argument('--debug', dest='debug', action='store_true')
    args = parser.parse_args()

    CONFIG['debug'] = True if args.debug else False
    CONFIG['port'] = int(args.port)

    with open(args.configfile, 'r') as fp:
        file_config = json.load(fp)
        CONFIG['db_filename'] = file_config['db_filename']

    CONFIG['source_dir'] = pkg_resources.resource_filename(__name__, "html")

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    logging.info('Starting daemon on port: %s' % args.port)
    logging.info('Serving files from: %s' % CONFIG['source_dir'])
    logging.info('JSON from: %s' % CONFIG['db_filename'])
    logging.debug('Debugging on')

    if not args.nodaemon:
        os.makedirs('/var/run/ptgbot', exist_ok=True)
        pid = daemon.pidfile.TimeoutPIDLockFile(
            '/var/run/ptgbot/ptgbot-web.pid', 10)
        with daemon.DaemonContext(pidfile=pid):
            start()
    start()


if __name__ == "__main__":
    main()