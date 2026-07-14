"""Initial migration - Create HCP and Interaction tables

Revision ID: 001
Revises: 
Create Date: 2024-07-14 12:52:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create hcps table
    op.create_table(
        'hcps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_name', sa.String(length=255), nullable=False),
        sa.Column('hospital', sa.String(length=255), nullable=False),
        sa.Column('specialization', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hcps_city'), 'hcps', ['city'], unique=False)
    op.create_index(op.f('ix_hcps_doctor_name'), 'hcps', ['doctor_name'], unique=False)
    op.create_index(op.f('ix_hcps_email'), 'hcps', ['email'], unique=True)
    op.create_index(op.f('ix_hcps_id'), 'hcps', ['id'], unique=False)
    op.create_index(op.f('ix_hcps_specialization'), 'hcps', ['specialization'], unique=False)

    # Create interactions table
    op.create_table(
        'interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hcp_id', sa.Integer(), nullable=False),
        sa.Column('interaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('discussion', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('follow_up_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['hcp_id'], ['hcps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interactions_hcp_id'), 'interactions', ['hcp_id'], unique=False)
    op.create_index(op.f('ix_interactions_id'), 'interactions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_interactions_id'), table_name='interactions')
    op.drop_index(op.f('ix_interactions_hcp_id'), table_name='interactions')
    op.drop_table('interactions')
    
    op.drop_index(op.f('ix_hcps_specialization'), table_name='hcps')
    op.drop_index(op.f('ix_hcps_email'), table_name='hcps')
    op.drop_index(op.f('ix_hcps_id'), table_name='hcps')
    op.drop_index(op.f('ix_hcps_doctor_name'), table_name='hcps')
    op.drop_index(op.f('ix_hcps_city'), table_name='hcps')
    op.drop_table('hcps')
