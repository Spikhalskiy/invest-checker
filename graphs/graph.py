from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Numeric, String, DateTime

Base = declarative_base()


class GraphPoint(Base):
    __tablename__ = 'GraphPoints'
    date = Column(DateTime, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    value = Column(Numeric, nullable=False)

    def __str__(self):
        return "GraphPoint("+self.category+"){date="+str(self.date)+", name="+self.name+", value="+str(self.value)+"}"

    def __repr__(self):
        return "GraphPoint("+self.category+"){date="+str(self.date)+", name="+self.name+", value="+str(self.value)+"}"

