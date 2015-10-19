from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from restaurant_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import cgi

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content_type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Add new restaurant</h1>"
                output += ('''
                            <form
                                method='POST'
                                enctype='multipart/form-data'
                                action='/restaurants/new'>
                            <input name='newname' type='text'
                                placeholder='Restaurant Name'>
                            <input type='submit' value='Create'>
                            ''')
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
                query = (
                            session.query(Restaurant)
                            .order_by(Restaurant.name)
                            .all()
                )
                self.send_response(200)
                self.send_header('Content_type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += ('''
                            <p>
                            <a href='/restaurants/new'>
                            Add a new restaurant
                            </a>
                            </p>
                           ''')
                for row in query:
                    output += "<p>"
                    output += row.name
                    output += "<br />"
                    output += "<a href='#'>Edit</a> / "
                    output += "<a href='#'>Delete</a>"
                    output += "</p>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/test"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>Hello!"
                output += ('''
                            <form
                                method='POST'
                                enctype='multipart/form-data'
                                action='/test'>
                            <h2>What would you like me to say?</h2>
                                <input name='message' type='text'>
                                <input type='submit' value='Submit'>
                            </form>
                           ''')
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/testhola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += ('''
                            <html><body>&#161Hola
                            <a href = '/test'>Back to Hello</a>
                           ''')
                output += ('''
                            <form
                                method='POST'
                                enctype='multipart/form-data'
                                action='/test'>
                            <h2>What would you like me to say?</h2>
                                <input name='message' type='text'>
                                <input type='submit' value='Submit'>
                            </form>
                           ''')
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newname')

                # Create new Restaurant class
                new = Restaurant(name = messagecontent[0])
                session.add(new)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return
#            self.send_response(301)
#            self.end_headers()
#            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
#            if ctype == 'multipart/form-data':
#                fields = cgi.parse_multipart(self.rfile, pdict)
#                messagecontent = fields.get('message')
#            output = ""
#            output += "<html><body>"
#            output += "<h2>Okay, how about this:</h2>"
#            output += "<h1>%s</h1>" % messagecontent[0]
#            output += ('''
#                            <form
#                                method='POST'
#                                enctype='multipart/form-data'
#                                action='/test'>
#                            <h2>What would you like me to say?</h2>
#                                <input name='message' type='text'>
#                                <input type='submit' value='Submit'>
#                            </form>
#                       ''')
#            output += "</body></html>"
#            self.wfile.write(output)
#            print output

        except:
            pass


def main():
    try:
        port = 8090
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()


if __name__ == '__main__':
    main()
