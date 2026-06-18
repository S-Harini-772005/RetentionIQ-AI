from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 Declarative Mapping Base.
    Includes automated table naming convention.
    """
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Automatically generates table names based on class name in lowercase.
        """
        return cls.__name__.lower()

    def __repr__(self) -> str:
        """
        Standard representation for debugging and logging.
        """
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'n/a')})>"

# Instructions for Alembic:
# Import all project models here to register them with Base.metadata
# from app.database.models import User, Customer, RFMSegment, ChurnPrediction, etc.