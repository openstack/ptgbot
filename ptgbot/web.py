import argparse
import daemon
import daemon.pidfile
import http.server
import json
import logging
import os
import pkg_resources
import socketserver

import ptgbot.ics


CONFIG = {}


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('ptg.json'):
            with open(CONFIG['db_filename'], 'rb') as fp:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(fp.read())
        elif self.path.endswith('.ics'):
            team = os.path.basename(self.path)[:-4]
            with open(CONFIG['db_filename'], 'rb') as fp:
                ics = ptgbot.ics.json2ical(json.load(fp), team)
            self.send_response(200)
            self.send_header('Content-type', 'text/calendar')
            self.end_headers()
            self.wfile.write(ics)
        else:
            http.server.SimpleHTTPRequestHandler.do_GET(self)

    def log_message(self, format, *args):
        logging.debug("%s - - [%s] %s" % (self.address_string(),
                                          self.log_date_time_string(),
                                          format % args))


def start():
    os.chdir(CONFIG['source_dir'])
    # In a fast restart of the service we don't have time for all the TCP
    # sessions to drain the sockets in TIME_WAIT.  So the service fails to
    # restart with a "bind address in use".   To avoid this we want to add
    # SO_REUSEADDR and SO_REUSEPORT.  To do so we have to disable
    # bind_and_activate so we can then set allow_reuse_address and
    # allow_reuse_address on the TCPServer before we bind.
    with socketserver.TCPServer(("", CONFIG['port']), RequestHandler,
                                bind_and_activate=False) as httpd:
        httpd.allow_reuse_address = True
        httpd.allow_reuse_port = True
        httpd.server_bind()
        httpd.server_activate()
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
