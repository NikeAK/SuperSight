from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class Accounts(Base):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str]
    password: Mapped[str]
    proxy: Mapped[str]
    privatekey: Mapped[str]
    twitter_key: Mapped[str]
    crystals: Mapped[int] = mapped_column(nullable=True)
    
