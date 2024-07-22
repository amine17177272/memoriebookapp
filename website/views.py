from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Memorie, User, Like, PostForm
from . import db

views = Blueprint('views', __name__)

@views.route('/',methods=['GET', 'POST'])
@login_required
def home():
    return render_template('home.html', user=current_user)

@views.route('/main')
@login_required
def main():
    posts = Memorie.query.all()
    liked_posts = [like.post_id for like in current_user.likes]
    return render_template('index.html', user=current_user, posts=posts, liked_posts=liked_posts)

@views.route('/post', methods=['POST'])
@login_required
def add_post():
    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'error': 'Content is required'}), 400

    new_post = Memorie(data=content, user_id=current_user.id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created successfully'}), 201

@views.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Memorie.query.get_or_404(post_id)

    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if like:
        db.session.delete(like)
        db.session.commit()
        status = 'unliked'
    else:
        new_like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)
        db.session.commit()
        status = 'liked'

    # Re-query post to get updated like count
    post = Memorie.query.get_or_404(post_id)
    like_count = len(post.likes)

    return jsonify({'status': status, 'like_count': like_count})
@views.route('/post/<int:post_id>/delete', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = Memorie.query.get_or_404(post_id)
    
    # Check if the current user is authorized to delete the post
    if post.user_id != current_user.id:
        return jsonify({'error': 'You are not authorized to delete this post'}), 403

    # Delete all likes related to this post
    likes = Like.query.filter_by(post_id=post.id).all()
    for like in likes:
        db.session.delete(like)

    # Delete the post
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200
@views.route('/search')
@login_required
def search():
    username = request.args.get('username')
    if username:
        users = User.query.filter(User.user_name.ilike(f'%{username}%')).all()
        users_data = [{'id': user.id, 'user_name': user.user_name} for user in users]
        return jsonify({'users': users_data})
    return render_template('search.html', user=current_user)

@views.route('/user/<int:user_id>/posts')
@login_required
def get_user_posts(user_id):
    user = User.query.get(user_id)
    if user:
        posts = Memorie.query.filter_by(user_id=user_id).all()
        posts_data = [{'id': post.id, 'content': post.data, 'date': post.date.strftime('%Y-%m-%d'), 'likes': len(post.likes), 'liked': current_user.id in [like.user_id for like in post.likes]} for post in posts]
        return jsonify({'posts': posts_data})
    return jsonify({'posts': []})
