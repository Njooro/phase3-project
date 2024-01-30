from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from db import Base, session


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer(), primary_key=True)
    name = Column(String(), index=True)
    national_id = Column(Integer())
    location = Column(String())
    phone = Column(Integer())

    created_at = Column(DateTime(), server_default=func.now())
    updated_at = Column(DateTime(), onupdate=func.now())

    matatus = relationship('Matatu', back_populates='_member', cascade='all, delete-orphan')
    routes = association_proxy('matatus', '_route',
                                    creator=lambda rt: Matatu(route=rt))

    def __repr__(self):

        return f'Member(id = {self.id}, ' + \
            f'name = {self.name}, ' + \
            f'national_id = {self.national_id}, ' + \
            f'location = {self.location}, ' + \
            f'contact = +{self.phone})'
    

class Route(Base):
    __tablename__ = 'routes'

    id = Column(Integer(), primary_key=True)
    name = Column(String(), index=True)
    price = Column(Integer())

    created_at = Column(DateTime(), server_default=func.now())
    updated_at = Column(DateTime(), onupdate=func.now())

    matatus = relationship('Matatu', back_populates='_route', cascade='all, delete-orphan')
    members = association_proxy('matatus', '_member',
                                  creator=lambda mem: Matatu(member=mem))
    
    def __repr__(self):
        return f'Route(id = {self.id}, ' + \
            f'name = {self.name}, ' + \
            f'price = {self.price})'
    


class Matatu(Base):
    __tablename__ = 'matatus'

    id = Column(Integer(), primary_key=True)
    driver_name = Column(String())
    driver_contact = Column(Integer())
    number_plate = Column(String())
    capacity = Column(Integer())
    avg_rounds_pd = Column(Integer())
    member_id = Column(Integer())
    route_id = Column(Integer())    

    created_at = Column(DateTime(), server_default=func.now())
    updated_at = Column(DateTime(), onupdate=func.now())

    route_id = Column(Integer(), ForeignKey('routes.id'))
    member_id = Column(Integer(), ForeignKey('members.id'))

    _route = relationship('Route', back_populates='matatus')
    _member = relationship('Member', back_populates='matatus')

    def __repr__(self):
        return f'Matatu(id = {self.id}, ' + \
            f'driver_name = {self.driver_name}, ' + \
            f'driver_contact = +{self.driver_contact}, ' + \
            f'number_plate = {self.number_plate}, ' + \
            f'capacity = {self.capacity}, ' + \
            f'avg_rounds_pd = {self.avg_rounds_pd}, ' + \
            f'member_id = {self.member_id}, ' + \
            f'route_id = {self.route_id})'
