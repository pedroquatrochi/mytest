from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template ('index.html')

@app.route('/cad/usuario')
def usuario():
    return render_template ('usuario.html')

@app.route('/cad/caduser', methods=['post'])
def caduser():
    return request.form

@app.route('/cad/anuncio')
def anuncio():
    return render_template('anuncio.html')

@app.route('/anuncios/pergunta')
def pergunta():
    return render_template ('pergunta.html')

@app.route('/anuncios/compra')
def compra():
    print ('anúncio comprado')
    return ''

@app.route('/anuncios/favoritos')
def favoritos():
    print ('favorito inserido')
    return ''

@app.route('/config/categoria')
def categoria():
    return render_template ('categoria.html')

@app.route('/relatorios/vendas')
def relvendas():
    return render_template ('relavendas.html')

@app.route('/relatorios/compras')
def relcompras():
    return render_template ('relacompras.html')