"""empty message

Revision ID: 7adcf0226cd4
Revises: None
Create Date: 2016-06-04 15:45:45.532000

"""

# revision identifiers, used by Alembic.
revision = '7adcf0226cd4'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('connection',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('users_id', sa.Integer(), nullable=True),
    sa.Column('provider_id', sa.String(length=255), nullable=True),
    sa.Column('provider_user_id', sa.String(length=255), nullable=True),
    sa.Column('access_token', sa.String(length=255), nullable=True),
    sa.Column('secret', sa.String(length=255), nullable=True),
    sa.Column('display_name', sa.String(length=255), nullable=True),
    sa.Column('profile_url', sa.String(length=512), nullable=True),
    sa.Column('image_url', sa.String(length=512), nullable=True),
    sa.Column('rank', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('connection')
    ### end Alembic commands ###
