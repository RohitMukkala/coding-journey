"""update coding profiles table

Revision ID: update_coding_profiles
Revises: initial_migration
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'update_coding_profiles'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    # Drop existing coding_profiles table
    op.drop_table('coding_profiles')
    
    # Create new coding_profiles table with updated schema
    op.create_table(
        'coding_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        
        # GitHub specific fields
        sa.Column('total_contributions', sa.Integer(), nullable=True),
        sa.Column('current_streak', sa.Integer(), nullable=True),
        sa.Column('longest_streak', sa.Integer(), nullable=True),
        sa.Column('total_stars', sa.Integer(), nullable=True),
        sa.Column('total_forks', sa.Integer(), nullable=True),
        sa.Column('languages', postgresql.JSON(), nullable=True),
        
        # LeetCode specific fields
        sa.Column('total_problems_solved', sa.Integer(), nullable=True),
        sa.Column('easy_solved', sa.Integer(), nullable=True),
        sa.Column('medium_solved', sa.Integer(), nullable=True),
        sa.Column('hard_solved', sa.Integer(), nullable=True),
        sa.Column('easy_percentage', sa.Float(), nullable=True),
        sa.Column('medium_percentage', sa.Float(), nullable=True),
        sa.Column('hard_percentage', sa.Float(), nullable=True),
        
        # CodeChef specific fields
        sa.Column('current_rating', sa.Integer(), nullable=True),
        sa.Column('highest_rating', sa.Integer(), nullable=True),
        sa.Column('global_rank', sa.Integer(), nullable=True),
        sa.Column('country_rank', sa.Integer(), nullable=True),
        sa.Column('stars', sa.Integer(), nullable=True),
        
        # CodeForces specific fields
        sa.Column('codeforces_rating', sa.Integer(), nullable=True),
        sa.Column('codeforces_max_rating', sa.Integer(), nullable=True),
        sa.Column('problems_solved_count', sa.Integer(), nullable=True),
        sa.Column('contest_rating', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'platform', name='unique_user_platform')
    )
    
    # Create index for faster lookups
    op.create_index('idx_coding_profiles_user_platform', 'coding_profiles', ['user_id', 'platform'])

def downgrade():
    # Drop the new table
    op.drop_table('coding_profiles')
    
    # Recreate the original table
    op.create_table(
        'coding_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('profile_link', sa.String(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    ) 