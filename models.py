from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)
    description = Column(String(1000))
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id':           self.id,
            'name':         self.name,
            'description':  self.description,
        }


class Breed(Base):
    __tablename__ = 'breed'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(1000))
    height = Column(String(100))
    weight = Column(String(100))
    picture = Column(String(250))
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship(Group)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id':           self.id,
            'name':         self.name,
            'description':  self.description,
            'height':       self.height,
            'weight':       self.weight,
        }

engine = create_engine('sqlite:///dogbreeds.db')

Base.metadata.create_all(engine)
