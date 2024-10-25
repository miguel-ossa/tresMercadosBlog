from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class CreatePostForm(FlaskForm):
    """
    Formulario de creación de publicaciones de blog.

    Este formulario define los campos necesarios para crear una nueva publicación de blog,
    incluyendo título, subtítulo, URL de la imagen, contenido y un botón de envío.

    Campos:
        title (StringField): Campo de texto para el título de la publicación.
        subtitle (StringField): Campo de texto para el subtítulo de la publicación.
        img_url (StringField): Campo de texto para la URL de la imagen de la publicación.
        body (CKEditorField): Campo de texto enriquecido para el contenido de la publicación.
        submit (SubmitField): Botón de envío para enviar el formulario.
    """
    title = StringField("Título do post do blogue", validators=[DataRequired()])
    subtitle = StringField("Subtítulo", validators=[DataRequired()])
    img_url = StringField("URL da imagem do blogue", validators=[DataRequired(), URL()])
    body = CKEditorField("Conteúdo do blogue", validators=[DataRequired()])
    submit = SubmitField("Enviar Post")


class RegisterForm(FlaskForm):
    """
    Formulario de registro de nuevos usuarios.

    Este formulario define los campos necesarios para registrar un nuevo usuario,
    incluyendo correo electrónico, contraseña y nombre.

    Campos:
        email (StringField): Campo de texto para el correo electrónico del usuario.
        password (PasswordField): Campo de contraseña para la contraseña del usuario.
        name (StringField): Campo de texto para el nombre del usuario.
        submit (SubmitField): Botón de envío para enviar el formulario.
    """
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Palavra-passe", validators=[DataRequired()])
    name = StringField("Nome", validators=[DataRequired()])
    submit = SubmitField("Regista-me!")


class LoginForm(FlaskForm):
    """
    Formulario de inicio de sesión de usuarios existentes.

    Este formulario define los campos necesarios para iniciar sesión como usuario existente,
    incluyendo correo electrónico y contraseña.

    Campos:
        email (StringField): Campo de texto para el correo electrónico del usuario.
        password (PasswordField): Campo de contraseña para la contraseña del usuario.
        submit (SubmitField): Botón de envío para enviar el formulario.
    """
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Palavra-passe", validators=[DataRequired()])
    submit = SubmitField("Entrar")


class CommentForm(FlaskForm):
    """
    Formulario de creación de comentarios.

    Este formulario define el campo necesario para crear un nuevo comentario,
    incluyendo el texto del comentario.

    Campos:
        comment_text (CKEditorField): Campo de texto enriquecido para el texto del comentario.
        submit (SubmitField): Botón de envío para enviar el formulario.
    """
    comment_text = CKEditorField("Comentário", validators=[DataRequired()])
    submit = SubmitField("Enviar comentário")
