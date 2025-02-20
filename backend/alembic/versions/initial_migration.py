"""initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table with all fields
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('profile_picture', sa.String(), nullable=True),
        sa.Column('leetcode_username', sa.String(), nullable=True),
        sa.Column('github_username', sa.String(), nullable=True),
        sa.Column('codechef_username', sa.String(), nullable=True),
        sa.Column('codeforces_username', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Create coding_profiles table
    op.create_table(
        'coding_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('profile_link', sa.String(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('coding_profiles')
    op.drop_table('users') 