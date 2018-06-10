import subprocess
import atexit
import os
from flask import render_template, render_template_string, Flask
from bokeh.embed import autoload_server
from bokeh.client import pull_session
 
app_html="""
<!DOCTYPE html>
<html lang="en">
  <body>
    <p>This is the app</p>
    <div class="bk-root">
      {{ bokeh_script|safe }}
    </div>
  </body>
</html>
"""
 
app = Flask(__name__)
 
bokeh_process = subprocess.Popen(
    ['bokeh', 'serve','--allow-websocket-origin=localhost:5000','bokeh_plot.py'], stdout=subprocess.PIPE)
 
@atexit.register
def kill_server():
    bokeh_process.kill()
 
@app.route("/")
def index():
    session=pull_session(app_path="/bokeh_plot")
    bokeh_script=autoload_server(None,app_path="/bokeh_plot",session_id=session.id)
    return render_template_string(app_html, bokeh_script=bokeh_script)
 
if __name__ == "__main__":
    print("STARTED")
    #port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port)
    app.run(debug=True)