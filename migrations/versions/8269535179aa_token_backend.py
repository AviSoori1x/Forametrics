"""token_backend

Revision ID: 8269535179aa
Revises: 
Create Date: 2018-09-30 16:12:16.945551

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8269535179aa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('facebooktokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('access_token_fb', sa.String(length=640), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('feed_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('link', sa.String(length=140), nullable=True),
    sa.Column('title', sa.String(length=140), nullable=True),
    sa.Column('industry', sa.String(length=140), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('feeds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('feedlink', sa.String(length=140), nullable=True),
    sa.Column('industry', sa.String(length=140), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('twittertokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('token', sa.String(length=640), nullable=True),
    sa.Column('token_secret', sa.String(length=640), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('businessName', sa.String(length=120), nullable=True),
    sa.Column('services', sa.String(length=120), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('zip_code', sa.Integer(), nullable=True),
    sa.Column('coreService', sa.String(length=120), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_coreService'), 'user', ['coreService'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('bestdicts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hourdic', sa.String(length=640), nullable=True),
    sa.Column('socialnetwork', sa.String(length=40), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_username', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['user_username'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bestdicts_timestamp'), 'bestdicts', ['timestamp'], unique=False)
    op.create_table('facebook_analytics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('u_username', sa.String(length=64), nullable=True),
    sa.Column('date_time', sa.DateTime(), nullable=True),
    sa.Column('n_followers', sa.Integer(), nullable=True),
    sa.Column('n_haha', sa.Integer(), nullable=True),
    sa.Column('n_sad', sa.Integer(), nullable=True),
    sa.Column('n_wow', sa.Integer(), nullable=True),
    sa.Column('n_love', sa.Integer(), nullable=True),
    sa.Column('n_angry', sa.Integer(), nullable=True),
    sa.Column('n_comments', sa.Integer(), nullable=True),
    sa.Column('n_likes', sa.Integer(), nullable=True),
    sa.Column('n_shares', sa.Integer(), nullable=True),
    sa.Column('n_reactions', sa.Integer(), nullable=True),
    sa.Column('n_engagement', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['u_username'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_facebook_analytics_date_time'), 'facebook_analytics', ['date_time'], unique=False)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('socialnetwork', sa.String(length=40), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('hour', sa.Integer(), nullable=True),
    sa.Column('minute', sa.Integer(), nullable=True),
    sa.Column('day', sa.Integer(), nullable=True),
    sa.Column('month', sa.Integer(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('ampm', sa.String(length=2), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_timestamp'), 'post', ['timestamp'], unique=False)
    op.create_table('twitter_analytics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('u_username', sa.String(length=64), nullable=True),
    sa.Column('date_time', sa.DateTime(), nullable=True),
    sa.Column('n_followers', sa.Integer(), nullable=True),
    sa.Column('n_favorites', sa.Integer(), nullable=True),
    sa.Column('n_retweets', sa.Integer(), nullable=True),
    sa.Column('n_tweets', sa.Integer(), nullable=True),
    sa.Column('n_engagement', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['u_username'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_twitter_analytics_date_time'), 'twitter_analytics', ['date_time'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_twitter_analytics_date_time'), table_name='twitter_analytics')
    op.drop_table('twitter_analytics')
    op.drop_index(op.f('ix_post_timestamp'), table_name='post')
    op.drop_table('post')
    op.drop_table('followers')
    op.drop_index(op.f('ix_facebook_analytics_date_time'), table_name='facebook_analytics')
    op.drop_table('facebook_analytics')
    op.drop_index(op.f('ix_bestdicts_timestamp'), table_name='bestdicts')
    op.drop_table('bestdicts')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_coreService'), table_name='user')
    op.drop_table('user')
    op.drop_table('twittertokens')
    op.drop_table('feeds')
    op.drop_table('feed_item')
    op.drop_table('facebooktokens')
    # ### end Alembic commands ###
