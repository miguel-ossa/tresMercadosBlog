from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Título do post do blogue", validators=[DataRequired()])
    subtitle = StringField("Subtítulo", validators=[DataRequired()])
    img_url = StringField("URL da imagem do blogue", validators=[DataRequired(), URL()])
    body = CKEditorField("Conteúdo do blogue", validators=[DataRequired()])
    submit = SubmitField("Enviar Post")


# Create a form to register new users
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Palavra-passe", validators=[DataRequired()])
    name = StringField("Nome", validators=[DataRequired()])
    submit = SubmitField("Regista-me!")


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Palavra-passe", validators=[DataRequired()])
    submit = SubmitField("Entrar")


# Create a form to add comments
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comentário", validators=[DataRequired()])
    submit = SubmitField("Enviar comentário")
