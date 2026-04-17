from __future__ import annotations
from datetime import UTC, datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

# actually defining our database models

class User(Base):
    __tablename__ = "users"

    # setting primary_key=True makes it auto-increment. I assume deleting doesn't decrement
    # presumably primary_key and/or index also automatically means it will be unique
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) # what is this mapped keyword?
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    
    # stored just filename, not actual path
    # decouples database from our file organisation
    # if tomorrow we reorganise our directories we only have to update 
    # here, not go in and update database
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None
    )

    # relationship
    # one User has many Posts 
    # automatically links to user's all posts
    posts: Mapped[list[Post]] = relationship(back_populates="author", cascade="all, delete-orphan")

    @property #keyword lets you access class methods like attributes, via object.method (i think)
    def image_path(self) -> str:
        if self.image_file:
            # recall self.image_file is just the file name as a string
            return f"/media/profile_pics/{self.image_file}"
        else:
            return "/static/profile_pics/default.jpg"
        
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    # Text = ?
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        # each Post must have associated valid ForeignKey
        # without indexes, database scans each row manually to find desired row
        # primary keys get index automatically
        # foreign keys don't get index automatically
        # reads will be faster, writes will be slower but worth it
        # we will likely be quering post by user_id pretty frequently

        #A one to many relationship places a foreign key on 
        # the child table referencing the parent. relationship() 
        # is then specified on the parent, as referencing a 
        # collection of items represented by the child.

        #To establish a bidirectional relationship in 
        # one-to-many, where the “reverse” side is a 
        # many to one, specify an additional relationship() 
        # and connect the two using the relationship.back_populates 
        # parameter, using the attribute name of each relationship() 
        # as the value for relationship.back_populates on the other:
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    # does it associate to the correct user via user_id foreign key?
    # yes
    author: Mapped[User] = relationship(back_populates="posts")