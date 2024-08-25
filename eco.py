from flask import Flask, render_template, request, redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (current_user, LoginManager,
                             login_user, logout_user,
                             login_required)
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://pidrito:toledo22@localhost:3306/meubanco'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://quatrochi:toledo22@quatrochi.mysql.pythonanywhere-services.com:3306/quatrochi$meubanco'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = '258369'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(db.Model):
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(155))
    email = db.Column('usu_email', db.String(155))
    senha = db.Column('usu_senha', db.String(155))
    end = db.Column('usu_end', db.String(155))

    def __init__(self, nome, email, senha, end):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.end = end

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(155))
    desc = db.Column('cat_desc', db.String(155))

    def __init__ (self, nome, desc):
        self.nome = nome
        self.desc = desc

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anu_id', db.Integer, primary_key=True)
    nome = db.Column('anu_nome', db.String(256))
    desc = db.Column('anu_desc', db.String(256))
    qtd = db.Column('anu_qtd', db.Integer)
    preco = db.Column('anu_preco', db.Float)
    cat_id = db.Column('cat_id',db.Integer, db.ForeignKey("categoria.cat_id"))
    usu_id = db.Column('usu_id',db.Integer, db.ForeignKey("usuario.usu_id"))

    categoria = db.relationship('Categoria', backref=db.backref('anuncios', lazy=True))
    def __init__(self, nome, desc, qtd, preco, cat_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.cat_id = cat_id
        self.usu_id = usu_id

class Compra(db.Model):
    __tablename__ = 'compra'
    
    id = db.Column('comp_id', db.Integer, primary_key=True)
    usuario_id = db.Column('usu_id', db.Integer, db.ForeignKey('usuario.usu_id'), nullable=False)
    anuncio_id = db.Column('anu_id', db.Integer, db.ForeignKey('anuncio.anu_id'), nullable=False)
    quantidade = db.Column('comp_qtd', db.Integer, nullable=False)
    data_compra = db.Column('comp_data', db.DateTime, default=db.func.current_timestamp())

    # Relacionamento com a tabela Usuario
    usuario = db.relationship('Usuario', backref=db.backref('compras', lazy=True))
    
    # Relacionamento com a tabela Anuncio
    anuncio = db.relationship('Anuncio', backref=db.backref('compras', lazy=True))
    
    def __init__(self, usuario_id, anuncio_id, quantidade):
        self.usuario_id = usuario_id
        self.anuncio_id = anuncio_id
        self.quantidade = quantidade

class Pergunta(db.Model):
    __tablename__ = 'pergunta'
    
    id = db.Column('perg_id', db.Integer, primary_key=True)
    anuncio_id = db.Column('anu_id', db.Integer, db.ForeignKey('anuncio.anu_id'), nullable=False)
    usuario_id = db.Column('usu_id', db.Integer, db.ForeignKey('usuario.usu_id'), nullable=False)
    pergunta = db.Column('perg_texto', db.String(512), nullable=False)
    data_pergunta = db.Column('perg_data', db.DateTime, default=db.func.current_timestamp())

    anuncio = db.relationship('Anuncio', backref=db.backref('perguntas', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('perguntas', lazy=True))

    def __init__(self, anuncio_id, usuario_id, pergunta):
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id
        self.pergunta = pergunta

class Resposta(db.Model):
    __tablename__ = 'resposta'
    
    id = db.Column('resp_id', db.Integer, primary_key=True)
    pergunta_id = db.Column('perg_id', db.Integer, db.ForeignKey('pergunta.perg_id'), nullable=False)
    usuario_id = db.Column('usu_id', db.Integer, db.ForeignKey('usuario.usu_id'), nullable=False)
    resposta = db.Column('resp_texto', db.String(512), nullable=False)
    data_resposta = db.Column('resp_data', db.DateTime, default=db.func.current_timestamp())

    pergunta = db.relationship('Pergunta', backref=db.backref('respostas', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('respostas', lazy=True))

    def __init__(self, pergunta_id, usuario_id, resposta):
        self.pergunta_id = pergunta_id
        self.usuario_id = usuario_id
        self.resposta = resposta

class Favorito(db.Model):
    __tablename__ = 'favorito'
    
    id = db.Column('fav_id', db.Integer, primary_key=True)
    usuario_id = db.Column('usu_id', db.Integer, db.ForeignKey('usuario.usu_id'), nullable=False)
    anuncio_id = db.Column('anu_id', db.Integer, db.ForeignKey('anuncio.anu_id'), nullable=False)

    usuario = db.relationship('Usuario', backref=db.backref('favoritos', lazy=True))
    anuncio = db.relationship('Anuncio', backref=db.backref('favoritos', lazy=True))

    def __init__(self, usuario_id, anuncio_id):
        self.usuario_id = usuario_id
        self.anuncio_id = anuncio_id

@app.errorhandler(404)
def paginainexistente(error):
    return render_template('paginex.html')

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(int(id))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = Usuario.query.filter_by(email=email, senha=senha).first()

        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    anuncios = Anuncio.query.all()
    return render_template('index.html', anuncios=anuncios)

@app.route('/cad/usuario')
@login_required
def usuario():
    usuarios = Usuario.query.all()  # Obter todos os usuários do banco de dados
    return render_template('usuario.html', usuarios=usuarios, titulo='Cadastro de Usuario')

@app.route("/usuario/criar", methods=['POST'])
def criarusuario():
    hash = hashlib.sha512(str(request.form.get('senha')).encode('utf-8')).hexdigest()
    usuario = Usuario(request.form.get('user'), request.form.get('email'),hash, request.form.get('end'))
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/usuario/detalhar/<int:id>")
def buscarusuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route("/usuario/editar/<int:id>", methods=['GET','POST'])
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('user')
        usuario.email = request.form.get('email')
        usuario.senha = hashlib.sha512(str(request.form.get('senha')).encode('utf-8')).hexdigest()
        usuario.end = request.form.get('end')
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('usuario'))
    return render_template('edituser.html', usuario = usuario, titulo="Usuario")
    
@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuario')) 

@app.route("/cad/anuncio")
def anuncio():
    return render_template('anuncio.html', anuncios = Anuncio.query.all(), categorias = Categoria.query.all(), titulo="Anuncio")

@app.route("/anuncio/criar", methods=['POST'])
def criaranuncio():
    anuncio = Anuncio(request.form.get('nome'), request.form.get('desc'),request.form.get('qtd'),request.form.get('preco'),request.form.get('cat'),request.form.get('uso'))
    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncio/editar/<int:id>", methods=['GET', 'POST'])
def editaranuncio(id):
    anuncio = Anuncio.query.get(id)
    if request.method == 'POST':
        anuncio.nome = request.form.get('nome')
        anuncio.desc = request.form.get('desc')
        anuncio.qtd = request.form.get('qtd')
        anuncio.preco = request.form.get('preco')
        anuncio.cat_id = request.form.get('cat')
        anuncio.usu_id = request.form.get('uso')
        
        db.session.commit()
        return redirect(url_for('anuncio'))
    return render_template('editanuncio.html', anuncio=anuncio, categorias=Categoria.query.all(), titulo="Editar Anúncio")

@app.route("/anuncio/deletar/<int:id>")
def deletaranuncio(id):
    anuncio = Anuncio.query.get(id)
    db.session.delete(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

@app.route('/anuncios/pergunta', methods=['GET', 'POST'])
@login_required
def pergunta():
    if request.method == 'POST':
        anuncio_id = request.form.get('anuncio')
        pergunta_texto = request.form.get('pergunta')
        nova_pergunta = Pergunta(anuncio_id=anuncio_id, usuario_id=current_user.id, pergunta=pergunta_texto)
        db.session.add(nova_pergunta)
        db.session.commit()
        flash('Sua pergunta foi enviada com sucesso!')
        return redirect(url_for('pergunta'))

    anuncios = Anuncio.query.all()
    return render_template('pergunta.html', anuncios=anuncios)

@app.route('/anuncios/compra', methods=['GET', 'POST'])
@login_required
def compra():
    if request.method == 'POST':
        anuncio_id = request.form.get('anuncio_id')
        quantidade_comprada = request.form.get('quantidade')
        anuncio = Anuncio.query.get_or_404(anuncio_id)
        
        if anuncio.qtd >= int(quantidade_comprada):
            anuncio.qtd -= int(quantidade_comprada)
            nova_compra = Compra(usuario_id=current_user.id, anuncio_id=anuncio_id, quantidade=quantidade_comprada)
            db.session.add(nova_compra)
            db.session.commit()
            flash('Compra realizada com sucesso!', 'success')
        else:
            flash('Quantidade insuficiente disponível.', 'danger')
        return redirect(url_for('compra'))
    
    anuncios = Anuncio.query.all()
    return render_template('compra.html', anuncios=anuncios, titulo="Comprar Anúncio")

@app.route('/favoritos')
@login_required
def favoritos_usuario():
    favoritos = Favorito.query.filter_by(usuario_id=current_user.id).all()
    compras = Compra.query.filter_by(usuario_id=current_user.id).all()
    
    compras_ids = {compra.anuncio_id for compra in compras}
    
    return render_template('favoritos.html', favoritos=favoritos, compras_ids=compras_ids)

@app.route('/adicionar_favorito/<int:anuncio_id>', methods=['POST'])
@login_required
def adicionar_favorito(anuncio_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    favorito_existente = Favorito.query.filter_by(usuario_id=current_user.id, anuncio_id=anuncio_id).first()
    if not favorito_existente:
        favorito = Favorito(usuario_id=current_user.id, anuncio_id=anuncio_id)
        db.session.add(favorito)
        db.session.commit()
        flash('Anúncio adicionado aos favoritos!', 'success')
    else:
        flash('Anúncio já está na lista de favoritos.', 'info')
    
    return redirect(url_for('index'))

@app.route("/config/categoria")
def categoria():
    return render_template('categoria.html', categorias = Categoria.query.all(), titulo='Categoria')

@app.route("/categoria/criar", methods=['POST'])
def criarcategoria():
    categoria = Categoria(request.form.get('nome'), request.form.get('desc'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route("/categoria/editar/<int:id>", methods=['GET', 'POST'])
def editarcategoria(id):
    categoria = Categoria.query.get(id)
    if request.method == 'POST':
        categoria.nome = request.form.get('nome')
        categoria.desc = request.form.get('desc')
        db.session.commit()
        return redirect(url_for('categoria'))
    return render_template('editcategoria.html', categoria=categoria, titulo="Categoria")

@app.route("/categoria/deletar/<int:id>")
def deletarcategoria(id):
    categoria = Categoria.query.get(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route('/relatorios/vendas')
@login_required
def relvendas():
    # Consultar todas as vendas feitas pelo usuário logado
    vendas = Compra.query.filter_by(usu_id=current_user.id).all()
    return render_template('relavendas.html', vendas=vendas, titulo="Relatório de Vendas")

@app.route('/relatorios/compras')
@login_required
def relcompras():
    # Consultar todas as compras feitas pelo usuário logado
    compras = Compra.query.filter_by(usu_id=current_user.id).all()
    return render_template('relacompras.html', compras=compras, titulo="Relatório de Compras")

if __name__ == 'eco':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
