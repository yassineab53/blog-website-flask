from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User ,Comment ,EditPostForm 
from . import db



views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@views.route("/ajouter_post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post ne peut pas être vide ', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post crée!', category='success')
            return redirect(url_for('views.home'))

    return render_template('ajouter_post.html', user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first() #check s'il ya un post qui a cet id

    if not post:
        flash("Post n'existe pas.", category='error')
    elif current_user.id == post.id: #si c'est le user qui a crée le post 
        flash("vous n'avez pas la pérmission pour supprimer ce post .", category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post supprimé.', category='success')

    return redirect(url_for('views.home'))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("il n'existe aucun utilisateur avec ce username ", category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route('/posts')
@login_required
def posts_list():
    keyword = request.args.get('q')
    username = request.args.get('username')

    if keyword:
        posts = Post.query.filter(Post.text.ilike(f"%{keyword}%")).all()
        title = f'Les Posts avec "{keyword}"'
    elif username:
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Il n'existe aucun utilisateur avec cet username.", category='error')
            return redirect(url_for('views.home'))
        posts = user.posts
        title = f"Les Posts de {username}"
    else:
        posts = Post.query.all()
        title = "All Posts"

    return render_template('posts.html', posts=posts, title=title,user=current_user)



@views.route("/delete-profile/<int:user_id>", methods=['POST'])
@login_required
def delete_profile(user_id):
    if current_user.id == user_id:
        user = User.query.get(user_id)
        if user:
            #supprimer les posts du user 
            Post.query.filter_by(author=user_id).delete()
            
            # apès supprimer le user
            db.session.delete(user)
            db.session.commit()
            
            flash("votre compte et vos posts associés ont été bien supprimés.", category='success')
            return redirect(url_for('views.home'))
        else:
            flash("User n'existe pas.", category='error')
    else:
        flash("vous avez pas la permission de supprimer ce compte.", category='error')

    return redirect(url_for('views.home'))

@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))



@views.route("/delete-comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))

@views.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = EditPostForm()

    if form.validate_on_submit():
        post.text = form.text.data  
        db.session.commit()
        flash('Post mis à jour avec succès.', 'success')
        return redirect(url_for('views.edit_post', post_id=post.id))

    form.text.data = post.text  
    return render_template('edit_post.html', form=form, post=post, post_id=post_id, user=current_user)






