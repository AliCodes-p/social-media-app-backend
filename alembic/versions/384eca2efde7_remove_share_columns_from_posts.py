"""remove share columns from posts

Revision ID: 384eca2efde7
Revises: 3c7588450219
Create Date: 2026-07-06 12:59:15.046602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '384eca2efde7'
down_revision: Union[str, Sequence[str], None] = '3c7588450219'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint(
        "fk_posts_original_post",
        "posts",
        type_="foreignkey",
    )

    op.drop_column("posts", "original_post_id")
    op.drop_column("posts", "is_share")


def downgrade():
    op.add_column(
        "posts",
        sa.Column(
            "is_share",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "posts",
        sa.Column(
            "original_post_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_posts_original_post",
        "posts",
        "posts",
        ["original_post_id"],
        ["id"],
    )

    op.alter_column(
        "posts",
        "is_share",
        server_default=None,
    )
