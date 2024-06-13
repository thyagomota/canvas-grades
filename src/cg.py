import os
import sys
import re 
from model import Assignment, Student, Grade
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, NoResultFound

DATA_FOLDER = 'data'
session = None

def menu(): 
    print('1. Canvas Pull')
    print('2. GitHub Classroom Sync')
    print('3. Grading Updates')
    print('4. Canvas Push')
    print('5. Exit')

def canvas_file_select() -> str: 
    canvas_files = os.listdir(DATA_FOLDER)
    print('Select file to pull from the list below:')
    canvas_files.sort(key=lambda x: os.path.getctime(os.path.join(DATA_FOLDER, x)), reverse=True)
    for seq, name in enumerate(canvas_files): 
        print(f'{seq+1}. {name}')
    select = int(input('? '))
    return canvas_files[select-1]

def canvas_pull(canvas_file):
    with open(os.path.join(DATA_FOLDER, canvas_file), 'rt') as file: 
        headers = file.readline().strip().split(',')[5:]
        pp = file.readline().strip().split(',')[5:]
        assignments = []
        for i, header in enumerate(headers): 
            if pp[i] == '(read only)':
                break
            name, _ = header.split(' ')
            id = re.findall(r'\(([^()]+)\)', header)[0]
            assignment = Assignment(id=id, name=name)
            assignments.append(assignment)
            try: 
                session.add(assignment)
                session.commit()
            except IntegrityError: 
                session.rollback()
        for line in file: 
            line = line.strip().replace('"', '')
            last, first, id, sis_user_id, sis_login_id, section = line.split(',')[:6]
            first = first.strip()
            last = last.strip()
            student = Student(id=id, sis_user_id=sis_user_id, sis_login_id=sis_login_id,section=section,first=first,last=last)
            # print(f'{last},{first},{id},{sis_user_id},{sis_login_id},{section}')
            try: 
                session.add(student)
                session.commit()
            except IntegrityError: 
                session.rollback()
            for i, value in enumerate(line.split(',')[6:]):
                # print(f'{i},{value}')
                if i >= len(assignments) or len(value) == 0: 
                    break
                try: 
                    grade = session.query(Grade).filter(Grade.student_id == id, Grade.assignment_id == assignments[i].id).one()
                    grade.grade = float(value)
                    session.commit()
                except NoResultFound: 
                    grade = Grade(student_id=id, assignment_id=assignments[i].id, grade=float(value))
                    session.add(grade)
                    session.commit() 

def github_classroom_sync(github_classroom_file): 
    with open(os.path.join(DATA_FOLDER, github_classroom_file), 'rt') as file: 
        file.readline() # ignore headers
        for line in file: 
            line = line.strip()
            line = line.replace('"', '')
            identifier, github_username, github_id, name = line.split(',')
            first = identifier[:identifier.find(' ')]
            last = identifier[identifier.find(' ')+1:]
            try: 
                student = session.query(Student).filter(Student.first == first, Student.last == last).one() 
                student.github = github_username      
                session.commit() 
            except NoResultFound: 
                pass  

def get_student_id(github): 
    try: 
        student = session.query(Student).filter(Student.github == github).one() 
        return student.id 
    except NoResultFound: 
        return None
    
def get_student(student_id): 
    try: 
        student = session.query(Student).filter(Student.id == student_id).one() 
        return student
    except NoResultFound: 
        return None

def grades_update(assignment_id): 
    with open(os.path.join(DATA_FOLDER, f'{assignment_id}.csv'), 'rt') as file: 
        for line in file: 
            line = line.strip()
            github, value = line.split(',')
            student_id = get_student_id(github)
            try: 
                grade = session.query(Grade).filter(Grade.student_id == student_id, Grade.assignment_id == assignment_id).one()
                grade.grade = float(value)
                session.commit()
            except NoResultFound: 
                grade = Grade(student_id=student_id, assignment_id=assignment_id, grade=float(value))    
                session.add(grade)
                session.commit()

def get_assignment_name(assignment_id): 
    try: 
        assignment = session.query(Assignment).filter(Assignment.id == assignment_id).one() 
        return assignment.name
    except NoResultFound: 
        return None

def canvas_push(assignment_id): 
    assignment_name = get_assignment_name(assignment_id)
    if assignment_name: 
        with open(os.path.join(DATA_FOLDER, f'canvas-{assignment_id}.csv'), 'wt') as file: 
            file.write(f'Student,ID,SIS User ID,SIS Login ID,Section,{assignment_name} ({assignment_id})\n')
            grades = session.query(Grade).filter(Grade.assignment_id == assignment_id).all()
            for grade in grades: 
                student = get_student(grade.student_id)
                file.write(f'"{student.last}, {student.first}",{grade.student_id},{student.sis_user_id},{student.sis_login_id},{student.section},{grade.grade}\n')

if __name__ == "__main__":

    # db connection 
    engine = create_engine('sqlite:///cg.db')
    if not engine: 
        print('Couldn\'t connect with cg.db!')
        exit(1)
    Session = sessionmaker(engine)
    session = Session()

    option = -1
    while option != 5: 
        menu()
        option = int(input('? '))
        if option == 1:
            print('Canvas Pull')
            canvas_file = canvas_file_select()
            canvas_pull(canvas_file)
        elif option == 2: 
            print('GitHub Classroom Sync')
            github_classroom_sync('cs3810.csv')
        elif option == 3: 
            print('Grades Update')
            assignment_id = int(input('Assignment id? '))
            grades_update(assignment_id)
        elif option == 4: 
            print('Canvas Push')
            assignment_id = int(input('Assignment id? '))
            canvas_push(assignment_id)
        