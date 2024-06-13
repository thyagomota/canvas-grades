from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, create_engine, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

Base = declarative_base()

class Student(Base):
    __tablename__ = 'Students'
    id = Column(Integer, primary_key=True)
    sis_user_id = Column(Integer)
    sis_login_id = Column(String)
    section = Column(String)
    first = Column(String)
    last = Column(String)
    github = Column(String)
    grades = relationship("Grade", primaryjoin="Student.id==Grade.student_id")

class Assignment(Base): 
    __tablename__ = 'Assignments'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Grade(Base):
    __tablename__ = 'Grades'
    student_id = Column(Integer, ForeignKey("Students.id"), primary_key=True)
    assignment_id = Column(Integer, ForeignKey("Assignments.id"), primary_key=True)
    grade = Column(Float)

if __name__ == "__main__":
    engine = create_engine('sqlite:///cg.db')
    if engine: 
        Base.metadata.create_all(engine)
        print('cg database created!')