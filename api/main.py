import os
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, jsonify
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from doubleLinkedList import DoubleLinkedList
import logging

logging.basicConfig(level=logging.DEBUG)

# TODO: traducir las fechas del inglés al portugués, al mostrarlas en el HTML

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:

pip install pipreqs
pipreqs --force /path/to/project

python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

class AppConfig:
    """
    Clase de configuración de la aplicación Flask.

    Esta clase se encarga de obtener las credenciales para la aplicación y la base de datos,
    inicializar las extensiones de Flask utilizadas en la aplicación y proporcionar acceso
    a la instancia única de la aplicación configurada.
    """
    def __init__(self):
        """
        Inicializa la instancia de la aplicación Flask y configura las extensiones.

        - Crea una instancia de la aplicación Flask.
        - Llama a los métodos privados `_configure_app` e `_init_extensions` para configurar la aplicación
          e inicializar las extensiones.
        """
        self.app = Flask(__name__)
        self._configure_app()
        self._init_extensions()

    def _configure_app(self):
        """
        Configura la aplicación Flask obteniendo las credenciales para la aplicación y la base de datos
        desde las variables de entorno.

        - Obtiene la clave secreta de la aplicación y la cadena de conexión a la base de datos
          desde las variables de entorno 'FLASK_KEY' y 'DB_URI' respectivamente.
        - Configura la clave secreta y la cadena de conexión a la base de datos en la aplicación Flask.
        """
        self.app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')

    def _init_extensions(self):
        """
        Inicializa las extensiones de Flask utilizadas en la aplicación.

        - Inicializa las extensiones CKEditor, Bootstrap5, LoginManager y Gravatar para la aplicación Flask.
        - Configura el tamaño, calificación e imagen predeterminada para Gravatar.
        """
        self.ckeditor = CKEditor(self.app)
        self.bootstrap = Bootstrap5(self.app)
        self.login_manager = LoginManager(self.app)
        # For adding profile images to the comment section
        self.gravatar = Gravatar(self.app, size=100, rating='g', default='retro')
        self.engine = create_engine(os.environ.get('DB_URI'), pool_pre_ping=True)

    def get_login_manager(self):
        """
        Devuelve el administrador de inicio de sesión de Flask-Login.

        Retorna:
            LoginManager: Administrador de inicio de sesión de Flask-Login.
        """
        return self.login_manager

    def get_engine(self):
        """
        Devuelve el motor de la base de datos.

        Retorna:
            Engine: Motor de la base de datos creado con create_engine.
        """
        return self.engine

    def get_app(self):
        """
        Devuelve la instancia de la aplicación Flask.

        Retorna:
            Flask: Instancia de la aplicación Flask configurada.
        """
        return self.app

# Instancia única de la aplicación configurada
app_config = AppConfig()
app = app_config.get_app()

# Configure Flask-Login and the BD
login_manager = app_config.get_login_manager()
login_manager.init_app(app)
engine = app_config.get_engine()

def connect_db():
    """
    Establece una conexión con la base de datos.

    Esta función intenta establecer una conexión con la base de datos utilizando el motor de
    base de datos configurado. Si se produce un error, se registra un mensaje de error en el log.

    Args:
        None

    Returns:
        None

    Raises:
        SQLAlchemyError: Si ocurre un error al conectar con la base de datos.
    """
    try:
        engine.connect()
    except SQLAlchemyError as e:
        logging.error(f"Erro ao ligar à base de dados: {e}")


@login_manager.user_loader
def load_user(user_id):
    """
    Carga un usuario de la base de datos.

    Esta función es utilizada por Flask-Login para cargar un usuario a partir de su ID.

    Args:
        user_id (int): El ID del usuario a cargar.

    Returns:
        User: Un objeto de usuario si se encuentra, de lo contrario, devuelve None.
    """
    return db.get_or_404(User, user_id)

# CONNECT TO DB
# sqlite:///posts.db

# This parameter prevents the pool from using a particular connection that has passed a certain age,
# and is appropriate for database backends such as MySQL that automatically close connections
# that have been stale after a particular period of time
# engine = create_engine(os.environ.get('DB_URI'), pool_recycle=3600)

db = SQLAlchemy()
db.init_app(app)

# Configuración de tablas
# =======================
class BlogPost(db.Model):
    """
    Representa una publicación del blog.

    Esta clase define el modelo para una publicación del blog con sus atributos correspondientes.

    Atributos:
        id (int): Clave primaria de la publicación.
        author_id (int): Clave foránea que referencia el ID del autor (Usuario).
        author (User): Objeto relacionado con el usuario autor de la publicación.
        title (str): Título de la publicación (único e obligatorio).
        subtitle (str): Subtítulo de la publicación (obligatorio).
        date (str): Fecha de publicación (obligatorio).
        body (str): Contenido de la publicación (obligatorio).
        img_url (str): URL de la imagen de la publicación (obligatorio).
        comments (list[Comment]): Lista de comentarios asociados a la publicación.
    """
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # Parent relationship to the comments
    comments = relationship("Comment", back_populates="parent_post")


class User(UserMixin, db.Model):
    """
    Representa un usuario del blog.

    Esta clase define el modelo para un usuario del blog con sus atributos correspondientes
    e incluye la funcionalidad de autenticación.

    Atributos:
        id (int): Clave primaria del usuario.
        email (str): Correo electrónico del usuario (único y obligatorio).
        password (str): Contraseña del usuario (hasheada).
        name (str): Nombre del usuario.
        posts (list[BlogPost]): Lista de publicaciones creadas por el usuario.
        comments (list[Comment]): Lista de comentarios realizados por el usuario.

    Métodos:
        authenticate(email, password): Comprueba la autenticación del usuario.
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    # This will act like a list of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    # Parent relationship: "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")

    @staticmethod
    def authenticate(email, password):
        """
        Comprueba si el correo electrónico y la contraseña del usuario coinciden con los almacenados.

        Args:
            email (str): Correo electrónico del usuario a autenticar.
            password (str): Contraseña del usuario a autenticar.

        Returns:
            User: Objeto User si la autenticación es correcta, None en caso contrario.
        """
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            return user
        return None

class Comment(db.Model):
    """
    Representa un comentario en una publicación del blog.

    Esta clase define el modelo para un comentario en una publicación del blog
    con sus atributos correspondientes.

    Atributos:
        id (int): Clave primaria del comentario.
        text (str): Texto del comentario (obligatorio).
        author_id (int): Clave foránea que referencia el ID del autor (Usuario).
        comment_author (User): Objeto relacionado con el usuario que realizó el comentario.
        post_id (int): Clave foránea que referencia el ID de la publicación asociada.
        parent_post (BlogPost): Objeto relacionado con la publicación a la que pertenece el comentario.
    """
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    # Child relationship:"users.id" The users refers to the tablename of the User class.
    # "comments" refers to the comments property in the User class.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    # Child Relationship to the BlogPosts
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")

with app.app_context():
    db.create_all()

# def list_users():
#     users = User.query.all()
#     user_list = []
#     for user in users:
#         user_list.append({
#             "id": user.id,
#             "email": user.email,
#             "name": user.name
#         })
#     return user_list
#
# @app.route('/users')
# def get_all_users():
#     users = list_users()
#     return jsonify(users)

# Create an admin-only decorator

class RoleChecker:
    """
    Clase auxiliar para verificar los permisos de los usuarios.

    Esta clase proporciona un método estático `is_admin` que verifica si el usuario actual
    está autenticado y tiene el ID 1 (considerado como administrador).

    Métodos estáticos:
        is_admin(): Comprueba si el usuario actual es administrador.

    Retorna:
        bool: True si el usuario actual está autenticado y tiene el ID 1, False en caso contrario.
    """
    @staticmethod
    def is_admin():
        """
        Comprueba si el usuario actual está autenticado y tiene el ID 1 (considerado como administrador).

        Esta función verifica si el usuario actual ha iniciado sesión y su ID corresponde al
        de un administrador.

        Retorna:
            bool: True si el usuario actual está autenticado y tiene el ID 1, False en caso contrario.

        Excepciones:
            AttributeError: Se lanza si no se puede acceder a la propiedad 'current_user'.
        """
        try:
            return current_user.is_authenticated and current_user.id == 1
        except AttributeError:
            return False

def admin_only(f):
    """
    Decorador que restringe la ejecución de una función a usuarios administradores.

    Este decorador verifica si el usuario actual es un administrador utilizando el método
    `is_admin` de la clase `RoleChecker`. Si el usuario no es administrador, se genera una
    excepción HTTP 403 (Forbidden).

    Args:
        f (function): La función a decorar.

    Retorna:
        function: La función decorada con la comprobación de permisos.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not RoleChecker.is_admin():
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

class FormFactory:
    """
    Clase auxiliar para crear formularios dinámicamente.

    Esta clase proporciona un método estático `create_form` que crea un formulario
    en función del tipo de formulario solicitado.

    Métodos estáticos:
        create_form(form_type): Crea un formulario del tipo especificado.

    Args:
        form_type (str): Tipo de formulario a crear ("post", "register", "login", "comment").

    Returns:
        Form: Instancia del formulario creado.

    Excepciones:
        ValueError: Se lanza si se solicita un tipo de formulario no válido.
    """
    @staticmethod
    def create_form(form_type):
        """
        Crea un formulario del tipo especificado.

        Esta función crea una instancia del formulario correspondiente al tipo
        solicitado. Los tipos de formulario válidos son "post", "register", "login" y "comment".

        Args:
            form_type (str): Tipo de formulario a crear ("post", "register", "login", "comment").

        Returns:
            Form: Instancia del formulario creado.

        Excepciones:
            ValueError: Se lanza si se solicita un tipo de formulario no válido.
        """
        if form_type == 'post':
            return CreatePostForm()
        elif form_type == 'register':
            return RegisterForm()
        elif form_type == 'login':
            return LoginForm()
        elif form_type == 'comment':
            return CommentForm()
        raise ValueError(f'Formulário inválido: {form_type}')

@app.route('/register', methods=["GET", "POST"])
def register():
    """
    Registra un nuevo usuario en la base de datos.

    Esta función maneja las solicitudes GET y POST para la ruta '/register'.

    Para solicitudes GET, renderiza la plantilla 'register.html' con un formulario de registro vacío.

    Para solicitudes POST, valida el formulario de registro enviado. Si la validación es exitosa,
    realiza las siguientes acciones:

    1. Conecta a la base de datos.
    2. Comprueba si el correo electrónico del usuario ya existe en la base de datos.
    3. Si el correo electrónico ya existe, muestra un mensaje de flash al usuario
       e lo redirecciona a la página de inicio de sesión.
    4. Si el correo electrónico no existe, genera un hash y sal de la contraseña del usuario.
    5. Crea una nueva instancia de la clase 'User' con los datos del formulario.
    6. Añade el nuevo usuario a la sesión de la base de datos.
    7. Guarda los cambios en la base de datos.
    8. Autentica al usuario con Flask-Login.
    9. Redirecciona al usuario a la página principal de publicaciones.

    Args:
        None

    Returns:
        template: La plantilla 'register.html' con el formulario o un mensaje de flash
                  dependiendo de la solicitud.
    """
    form = FormFactory.create_form('register')
    if form.validate_on_submit():

        connect_db()
        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))

        user = result.scalar()
        if user:
            # User already exists
            flash("Já se inscreveu com esse e-mail, inicie sessão em vez disso!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Gestiona el inicio de sesión de usuarios.

    Esta función maneja las solicitudes GET y POST para la ruta '/login'.

    Para solicitudes GET, renderiza la plantilla 'login.html' con un formulario de inicio de sesión vacío.

    Para solicitudes POST, valida el formulario de inicio de sesión enviado. Si la validación es exitosa,
    intenta autenticar al usuario en base a su correo electrónico y contraseña.

    Si la autenticación es exitosa, autentica al usuario con Flask-Login y lo redirecciona
    a la página principal de publicaciones.

    Si la autenticación falla, muestra un mensaje de flash al usuario
    indicando credenciales incorrectas.

    Args:
        None

    Returns:
        template: La plantilla 'login.html' con el formulario o un mensaje de flash
                  dependiendo de la solicitud.
    """
    form = FormFactory.create_form('login')
    if form.validate_on_submit():
        user = User.authenticate(form.email.data, form.password.data)
        if user:
            login_user(user)
            return redirect(url_for('get_all_posts'))
        flash('Credenciais incorrectas.')
    return render_template("login.html", form=form, current_user=current_user)

@app.route('/logout')
def logout():
    """
    Cierra la sesión del usuario actual.

    Esta función maneja las solicitudes GET para la ruta '/logout'.

    Llama a la función `logout_user` de Flask-Login para cerrar la sesión del usuario actual.

    Redirecciona al usuario a la página principal de publicaciones una vez cerrada la sesión.

    Args:
        None

    Returns:
        redirect: Redirecciona al usuario a la página principal de publicaciones.
    """
    logout_user()
    return redirect(url_for('get_all_posts'))


def convert_posts_to_dll(posts):
    """
    Convierte una lista de publicaciones (objetos Post) a una Lista Doblemente Enlazada.

    Esta función toma una lista de objetos Post y crea una nueva Lista Doblemente Enlazada (DLL)
    que contiene los identificadores (IDs) de las publicaciones.

    Args:
        posts (list[Post]): Lista de objetos Post.

    Returns:
        DoubleLinkedList: Una Lista Doblemente Enlazada que contiene los IDs de las publicaciones.
    """
    dll = DoubleLinkedList()
    [dll.append(item.id) for item in posts]
    logging.debug(dll.display())
    return dll


def load_posts():
    """
    Carga todas las publicaciones del blog desde la base de datos.

    Esta función se conecta a la base de datos y ejecuta una consulta para recuperar todas las
    publicaciones almacenadas en la tabla 'BlogPost'.

    Si la consulta se ejecuta con éxito, devuelve una lista con objetos Post.

    En caso de ocurrir un error al acceder a la base de datos, se registra un mensaje de error
    utilizando logging y se devuelve una lista vacía.

    Returns:
        list[BlogPost]: Lista de objetos Post con las publicaciones recuperadas, o una lista vacía
                        en caso de error.
    """
    connect_db()

    result = db.session.execute(db.select(BlogPost))
    try:
        posts = result.scalars().all()
    except SQLAlchemyError as e:
        logging.error(f"Erro ao carregar publicações: {e}")
        return []
    return posts


@app.route('/')
def get_all_posts():
    """
    Muestra la página principal con un listado de todas las publicaciones del blog.

    Esta función recupera todas las publicaciones del blog utilizando la función `load_posts`.

    A continuación, renderiza la plantilla 'index.html' pasando la lista de publicaciones
    y el usuario actual (si está autenticado) al contexto de la plantilla.

    Returns:
        template: La plantilla 'index.html' con la lista de publicaciones y el usuario actual.
    """
    posts = load_posts()
    return render_template("index.html", all_posts=posts, current_user=current_user)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    """
    Muestra una publicación específica del blog y permite agregar comentarios.

    Esta función maneja solicitudes GET y POST para la ruta '/post/<int:post_id>'.

    Para solicitudes GET, recupera la publicación solicitada por su ID utilizando `db.get_or_404`.
    Luego, convierte la lista completa de publicaciones a una Lista Doblemente Enlazada (DLL)
    para facilitar la navegación entre publicaciones cercanas. Busca el nodo correspondiente
    a la publicación solicitada en la DLL y extrae las publicaciones anterior y posterior (si
    existen).

    Además, crea un formulario para agregar comentarios utilizando `FormFactory` y solo permite
    comentar a usuarios autenticados. Si el formulario se valida y el usuario está autenticado,
    crea un nuevo objeto Comment y lo guarda en la base de datos.

    Finalmente, renderiza la plantilla 'post.html' pasando la publicación solicitada, las
    publicaciones anterior y posterior (si existen), el formulario de comentarios y el usuario
    actual al contexto de la plantilla.

    Args:
        post_id (int): ID de la publicación a mostrar.

    Returns:
        template: La plantilla 'post.html' con la publicación, comentarios, formulario y
                  posibles publicaciones anterior y posterior.
    """
    posts = load_posts()
    dll = convert_posts_to_dll(posts)

    requested_post = db.get_or_404(BlogPost, post_id)
    # Get the node for this post
    node = dll.get(requested_post.id)
    next_post = None
    prev_post = None
    try:
        if node.next_node is not None:
            next_post = node.next_node.data
        if node.prev_node is not None:
            prev_post = node.prev_node.data
    except AttributeError:
        pass
    # Add the CommentForm to the route
    comment_form = FormFactory.create_form('comment')
    # Only allow logged-in users to comment on posts
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("É necessário fazer login ou registar-se para comentar.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        connect_db()
        try:
            db.session.add(new_comment)
            db.session.commit()
        except SQLAlchemyError as e:
            logging.error(f'Erro ao adicionar comentário: {e}')

    return render_template("post.html", post=requested_post, next_post=next_post, prev_post=prev_post,
                           current_user=current_user, form=comment_form)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    """
    Crea una nueva publicación en el blog.

    Esta función restringida por el decorador `admin_only` permite a los usuarios
    administradores crear nuevas publicaciones en el blog.

    Para solicitudes GET, renderiza la plantilla 'make-post.html' con un formulario vacío
    para la creación de publicaciones.

    Para solicitudes POST, valida el formulario enviado. Si la validación es exitosa,
    crea una nueva instancia de la clase `BlogPost` con los datos del formulario
    y la guarda en la base de datos.

    En caso de ocurrir un error al acceder a la base de datos, se registra un mensaje
    de error utilizando logging.

    Finalmente, redirecciona al usuario a la página principal con el listado de publicaciones.

    Returns:
        template: La plantilla 'make-post.html' con el formulario o redirecciona a la página
                  principal.
    """
    form = FormFactory.create_form('post')
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        connect_db()
        try:
            db.session.add(new_post)
            db.session.commit()
        except SQLAlchemyError as e:
            logging.error(f'Erro ao adicionar post: {e}')

        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form, current_user=current_user)


# Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    """
    Edita una publicación existente del blog.

    Esta función restringida por el decorador `admin_only` permite a los usuarios
    administradores editar publicaciones existentes.

    Para solicitudes GET, recupera la publicación solicitada por su ID utilizando `db.get_or_404`.
    Luego, pre-rellena un formulario de edición con los datos actuales de la publicación.

    Para solicitudes POST, valida el formulario de edición enviado. Si la validación es exitosa,
    actualiza los datos de la publicación existente en la base de datos.

    Finalmente, redirecciona al usuario a la página de la publicación editada.

    Args:
        post_id (int): ID de la publicación a editar.

    Returns:
        template: La plantilla 'make-post.html' con el formulario pre-rellenado o redirecciona a
                  la página de la publicación editada.
    """
    connect_db()
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    """
    Elimina una publicación del blog.

    Esta función restringida por el decorador `admin_only` permite a los usuarios
    administradores eliminar publicaciones del blog.

    Recupera la publicación solicitada por su ID utilizando `db.get_or_404`.
    Luego elimina la publicación de la base de datos.

    En caso de ocurrir un error al acceder a la base de datos, se registra un mensaje
    de error utilizando logging.

    Finalmente, redirecciona al usuario a la página principal con el listado de publicaciones.

    Args:
        post_id (int): ID de la publicación a eliminar.

    Returns:
        redirect: Redirecciona al usuario a la página principal.
    """
    connect_db()
    try:
        post_to_delete = db.get_or_404(BlogPost, post_id)
        db.session.delete(post_to_delete)
        db.session.commit()
    except SQLAlchemyError as e:
        logging.error(f'Erro ao eliminar uma publicação: {e}')

    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    """
    Muestra la página "Acerca de".

    Esta función renderiza la plantilla 'about.html' que contiene información
    sobre el blog o sus creadores.

    Args:
        None

    Returns:
        template: La plantilla 'about.html'.
    """
    return render_template("about.html", current_user=current_user)


@app.route("/donate")
def donate():
    """
    Muestra la página de donaciones.

    Esta función renderiza la plantilla 'donativos.html' que contiene información sobre
    cómo realizar donaciones al blog (opcional).

    Args:
        None

    Returns:
        template: La plantilla 'donativos.html'.
    """
    return render_template("donativos.html", current_user=current_user)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """
    Muestra la página de contacto.

    Esta función renderiza la plantilla 'contact.html' que permite a los usuarios
    ponerse en contacto con los administradores del blog (opcional).

    Args:
        None

    Returns:
        template: La plantilla 'contact.html'.
    """
    return render_template("contact.html", current_user=current_user)


if __name__ == "__main__":
    app.run(port=5001)
    #app.run(debug=True, port=5001)
