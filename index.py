from sanic import Sanic
from config.site_config import sites
from log import writeLog
from seed import seed
from sanic.response import html, redirect
import jinja2
import asyncio

app = Sanic(__name__)
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
app.static('/static', './static')
config_file_path = 'config/site_config.py'

@app.route('/')
async def index(request):
    existing_sites = []
    for site in sites:
        if (site['passkey'] != ''):
            existing_sites.append(site)
    template = jinja_env.get_template('index.html')
    html_content = template.render(sites=sites, existing_sites=existing_sites)
    return html(html_content)
async def reseed():
  while True:
    seed()
    await asyncio.sleep(10)
@app.route('/submit', methods=['POST'])
async def submit(request):
    site_id = request.form.get('site')
    passkey = request.form.get('passkey')
    for site in sites:
        if site['id'] == int(site_id):
            print('Updating passkey for ' + site['siteName'])
            site['passkey'] = passkey
    with open(config_file_path, 'w', encoding='utf-8') as f:
        f.write('sites =' + str(sites))
    return redirect('/')
app.add_task(reseed())
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
